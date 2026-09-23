"""SAMPLE IMPLEMENTATION of the text editor tool.

This is the part Anthropic does NOT give you. When you declare

    {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}

the model knows how to *ask* for 4 commands. Making them happen is your job,
and this file is a complete, readable version of that job.

Claude sends you a dict like:

    {"command": "str_replace", "path": "/hello.py",
     "old_str": "helo", "new_str": "hello"}

...and you return a string describing what happened. That string becomes the
`tool_result` Claude reads next turn.

    view         path [, view_range]              -> contents / directory listing
    create       path, file_text                  -> create or overwrite
    str_replace  path, old_str, new_str           -> replace exactly one match
    insert       path, insert_line, insert_text   -> insert after a line
"""

import shutil
from pathlib import Path


class EditorError(Exception):
    """A problem Claude can fix by trying again.

    The agent loop turns this into a tool_result with is_error=True. It is a
    normal part of the conversation, not a crash. Good messages matter: Claude
    reads them and adjusts.
    """


class TextEditorTool:
    def __init__(self, root):
        # Everything happens inside this one folder.
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Entry point: the agent loop calls this with Claude's tool input.
    # ------------------------------------------------------------------
    def run(self, tool_input):
        commands = {
            "view": self.view,
            "create": self.create,
            "str_replace": self.str_replace,
            "insert": self.insert,
        }
        command = tool_input.get("command")
        if command not in commands:
            # Note there is no "delete", and no "undo_edit" in 20250728.
            raise EditorError(
                f"Unknown command '{command}'. Use: {', '.join(commands)}."
            )
        return commands[command](tool_input)

    # ------------------------------------------------------------------
    # SECURITY: `path` is text the model made up. Never trust it.
    # ------------------------------------------------------------------
    def _path(self, raw):
        if not raw:
            raise EditorError("'path' is required.")
        # Claude writes paths like "/hello.py". Treat them as relative to root.
        full = (self.root / str(raw).lstrip("/\\")).resolve()
        # .resolve() collapses "..", so this catches escape attempts.
        if full != self.root and not full.is_relative_to(self.root):
            raise EditorError(f"'{raw}' is outside the workspace. Refused.")
        return full

    def _name(self, path):
        """Show Claude a short path, never your real folder structure."""
        return "/" + path.relative_to(self.root).as_posix()

    def _read(self, path):
        if not path.exists():
            raise EditorError(f"{self._name(path)} does not exist.")
        if path.is_dir():
            raise EditorError(f"{self._name(path)} is a directory, not a file.")
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # 1. view
    # ------------------------------------------------------------------
    def view(self, cmd):
        path = self._path(cmd.get("path"))

        # A directory path means "list it".
        if path.is_dir():
            names = sorted(self._name(p) for p in path.iterdir())
            return "\n".join(names) if names else "(empty folder)"

        lines = self._read(path).splitlines()
        start, end = 1, len(lines)

        # Optional: Claude asks for just part of a big file.
        if cmd.get("view_range"):
            start, end = cmd["view_range"]
            if end == -1:                      # -1 means "to the end"
                end = len(lines)
            if start < 1 or end < start:
                raise EditorError(
                    f"view_range {cmd['view_range']} is invalid; "
                    f"file has {len(lines)} lines."
                )
            end = min(end, len(lines))

        # ALWAYS number the lines. `insert_line` is 1-based and `str_replace`
        # needs exact text -- unnumbered output leaves Claude guessing.
        return "\n".join(f"{n:5d}\t{lines[n - 1]}" for n in range(start, end + 1))

    # ------------------------------------------------------------------
    # 2. create
    # ------------------------------------------------------------------
    def create(self, cmd):
        path = self._path(cmd.get("path"))
        if "file_text" not in cmd:
            raise EditorError("'file_text' is required for create.")

        note = ""
        if path.exists():
            # create OVERWRITES. Version 20250728 dropped `undo_edit`, so if you
            # want undo, you keep the backup yourself -- like this.
            shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
            note = " (old version saved as .bak)"

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(cmd["file_text"], encoding="utf-8")
        return f"Wrote {self._name(path)}{note}."

    # ------------------------------------------------------------------
    # 3. str_replace  -- the one that trips people up
    # ------------------------------------------------------------------
    def str_replace(self, cmd):
        path = self._path(cmd.get("path"))
        old = cmd.get("old_str")
        new = cmd.get("new_str", "")          # missing new_str = delete the text
        if old is None:
            raise EditorError("'old_str' is required for str_replace.")

        text = self._read(path)
        hits = text.count(old)

        # THE RULE: exactly one match, or it's an error.
        if hits == 0:
            raise EditorError(
                "old_str not found. View the file and copy the text exactly, "
                "including indentation."
            )
        if hits > 1:
            raise EditorError(
                f"old_str matched {hits} times. Add surrounding lines so it "
                "matches only once."
            )

        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        line = text[: text.index(old)].count("\n") + 1
        return f"Replaced 1 match in {self._name(path)} at line {line}."

    # ------------------------------------------------------------------
    # 4. insert
    # ------------------------------------------------------------------
    def insert(self, cmd):
        path = self._path(cmd.get("path"))
        if "insert_line" not in cmd or "insert_text" not in cmd:
            raise EditorError("'insert_line' and 'insert_text' are required.")

        lines = self._read(path).splitlines()
        at = cmd["insert_line"]

        # 0 = before the first line. len(lines) = append at the end.
        if not 0 <= at <= len(lines):
            raise EditorError(f"insert_line must be 0..{len(lines)}, got {at}.")

        new_lines = cmd["insert_text"].splitlines()
        lines[at:at] = new_lines
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return f"Inserted {len(new_lines)} line(s) after line {at}."


# ----------------------------------------------------------------------
# Try the implementation on its own -- no API key needed.
#     python text_editor_tool.py
# ----------------------------------------------------------------------
if __name__ == "__main__":
    editor = TextEditorTool("workspace")

    print(editor.create({"command": "create", "path": "/demo.py",
                         "file_text": "def greet():\n    print('helo')\n"}))
    print(editor.view({"command": "view", "path": "/demo.py"}))
    print(editor.str_replace({"command": "str_replace", "path": "/demo.py",
                              "old_str": "helo", "new_str": "hello"}))
    print(editor.insert({"command": "insert", "path": "/demo.py",
                         "insert_line": 0, "insert_text": "# fixed by Claude"}))
    print(editor.view({"command": "view", "path": "/demo.py"}))

