"""Client-side implementation of the Anthropic *text editor* tool.

Every line in this file is code *you* own. The API never touches your disk.
Claude only asks -- via a `tool_use` block -- for one of four commands, and this
module carries it out inside a fixed sandbox directory:

    view         path [, view_range]      -> file contents or directory listing
    create       path, file_text          -> create/overwrite (with a .bak backup)
    str_replace  path, old_str, new_str   -> replace exactly one occurrence
    insert       path, insert_line, insert_text -> insert after a line number

The tool is *schema-less*: you declare it as
`{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}` and the
input shape above is built into the model. That is also why this file exists --
the shape is fixed, but the behaviour is entirely up to you.

SECURITY: `path` is untrusted model output. `_resolve()` canonicalises it and
refuses anything that escapes the sandbox root (`..`, symlinks, stray absolute
paths). Never pass the raw `path` value to `open()`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

MAX_VIEW_CHARS = 10_000


class EditorError(Exception):
    """A recoverable failure.

    The caller turns this into a `tool_result` with `is_error: True` so Claude
    can read the message and try something else. Raising it is *not* a crash --
    it is a normal part of the conversation.
    """


class TextEditorBackend:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # dispatch
    # ------------------------------------------------------------------
    def run(self, tool_input: dict) -> str:
        """Execute one text-editor command and return the text Claude will see."""
        command = tool_input.get("command")
        handlers = {
            "view": self._view,
            "create": self._create,
            "str_replace": self._str_replace,
            "insert": self._insert,
        }
        handler = handlers.get(command)
        if handler is None:
            raise EditorError(
                f"Unsupported command {command!r}. "
                f"Expected one of: {', '.join(handlers)}."
            )
        return handler(tool_input)

    # ------------------------------------------------------------------
    # path confinement -- the only security-critical function here
    # ------------------------------------------------------------------
    def _resolve(self, raw_path: str | None) -> Path:
        if not raw_path:
            raise EditorError("`path` is required.")
        # Claude often emits absolute-looking paths ("/notes.md"). Treat them as
        # sandbox-relative rather than rejecting them outright.
        candidate = (self.root / str(raw_path).lstrip("/\\")).resolve()
        if candidate != self.root and not candidate.is_relative_to(self.root):
            raise EditorError(
                f"Refused: {raw_path!r} resolves outside the sandbox root."
            )
        return candidate

    def _display(self, path: Path) -> str:
        """Path as shown back to Claude -- relative, so it never learns the real root."""
        return "/" + path.relative_to(self.root).as_posix() if path != self.root else "/"

    def _read(self, path: Path) -> str:
        if not path.exists():
            raise EditorError(f"File {self._display(path)} does not exist.")
        if path.is_dir():
            raise EditorError(f"{self._display(path)} is a directory, not a file.")
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # commands
    # ------------------------------------------------------------------
    def _view(self, tool_input: dict) -> str:
        path = self._resolve(tool_input.get("path"))

        if path.is_dir():
            entries = sorted(
                (("dir " if p.is_dir() else "file"), self._display(p))
                for p in path.iterdir()
            )
            if not entries:
                return f"{self._display(path)} is empty."
            listing = "\n".join(f"{kind}  {name}" for kind, name in entries)
            return f"Contents of {self._display(path)}:\n{listing}"

        lines = self._read(path).splitlines()
        start, end = 1, len(lines)

        view_range = tool_input.get("view_range")
        if view_range is not None:
            if not isinstance(view_range, list) or len(view_range) != 2:
                raise EditorError("`view_range` must be a [start, end] pair.")
            start, end = view_range
            if end == -1:
                end = len(lines)
            if not 1 <= start <= max(len(lines), 1) or end < start:
                raise EditorError(
                    f"`view_range` {view_range} is out of bounds; "
                    f"the file has {len(lines)} lines."
                )
            end = min(end, len(lines))

        # Line numbers matter: `str_replace` and `insert` both need Claude to
        # know where things are, and `insert_line` is 1-indexed.
        body = "\n".join(
            f"{n:6d}\t{lines[n - 1]}" for n in range(start, end + 1)
        )
        return body[:MAX_VIEW_CHARS]

    def _create(self, tool_input: dict) -> str:
        path = self._resolve(tool_input.get("path"))
        file_text = tool_input.get("file_text")
        if file_text is None:
            raise EditorError("`file_text` is required for `create`.")
        if path.is_dir():
            raise EditorError(f"{self._display(path)} is a directory.")

        note = ""
        if path.exists():
            # `create` overwrites. Keeping a backup is our choice, not the API's.
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            note = f" (previous version saved to {self._display(backup)})"

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file_text, encoding="utf-8")
        return f"Wrote {len(file_text)} characters to {self._display(path)}{note}."

    def _str_replace(self, tool_input: dict) -> str:
        path = self._resolve(tool_input.get("path"))
        old_str = tool_input.get("old_str")
        new_str = tool_input.get("new_str", "")
        if old_str is None:
            raise EditorError("`old_str` is required for `str_replace`.")

        content = self._read(path)
        count = content.count(old_str)
        # The contract is *exactly one* match. Reporting 0 or >1 as an error is
        # what lets Claude widen or narrow its snippet and retry.
        if count == 0:
            raise EditorError(
                f"`old_str` was not found in {self._display(path)}. "
                "View the file and copy the text exactly, including whitespace."
            )
        if count > 1:
            raise EditorError(
                f"`old_str` matched {count} times in {self._display(path)}. "
                "Include more surrounding context so it matches exactly once."
            )

        path.write_text(content.replace(old_str, new_str, 1), encoding="utf-8")
        line_no = content[: content.index(old_str)].count("\n") + 1
        return f"Replaced 1 occurrence in {self._display(path)} at line {line_no}."

    def _insert(self, tool_input: dict) -> str:
        path = self._resolve(tool_input.get("path"))
        insert_line = tool_input.get("insert_line")
        insert_text = tool_input.get("insert_text")
        if insert_line is None or insert_text is None:
            raise EditorError("`insert_line` and `insert_text` are both required.")

        lines = self._read(path).splitlines()
        # 0 means "before the first line"; len(lines) means "append".
        if not 0 <= insert_line <= len(lines):
            raise EditorError(
                f"`insert_line` must be between 0 and {len(lines)}, got {insert_line}."
            )

        new_lines = insert_text.splitlines() or [""]
        lines[insert_line:insert_line] = new_lines
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return (
            f"Inserted {len(new_lines)} line(s) into {self._display(path)} "
            f"after line {insert_line}."
        )
