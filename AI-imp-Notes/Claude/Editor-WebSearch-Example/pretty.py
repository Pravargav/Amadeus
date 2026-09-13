"""Print every content block the API returns, so nothing is invisible.

The whole point of the demos is to watch the block types go by. A response is a
*list* of content blocks, not a string, and the two tools show up as different
block types:

    text                      -> Claude talking
    thinking                  -> adaptive thinking (empty text unless display="summarized")
    tool_use                  -> CLIENT-side tool: your turn to act
    server_tool_use           -> SERVER-side tool: already ran on Anthropic's side
    web_search_tool_result    -> the search results themselves
"""

from __future__ import annotations

import json

RULE = "-" * 72


def show_response(response, label: str = "") -> None:
    header = f"[{response.stop_reason}]"
    if label:
        header = f"{label} {header}"
    print(f"\n{RULE}\n{header}\n{RULE}")

    for block in response.content:
        if block.type == "text":
            print(block.text)
            _show_citations(block)

        elif block.type == "thinking":
            # Default display is "omitted", so .thinking is usually "" -- the
            # block still exists and still has to be echoed back to the API.
            summary = (getattr(block, "thinking", "") or "").strip()
            print(f"(thinking block{': ' + summary[:200] if summary else ', omitted'})")

        elif block.type == "tool_use":
            # CLIENT-side. Nothing has happened yet; we must execute it.
            print(f"  -> tool_use  {block.name}  id={block.id}")
            print(f"     input: {json.dumps(block.input, indent=6)[:600]}")

        elif block.type == "server_tool_use":
            # SERVER-side. Already executed by the time we see it.
            print(f"  ~~ server_tool_use  {block.name}  input={block.input}")

        elif block.type == "web_search_tool_result":
            _show_search_result(block)

        else:
            print(f"  ?? unhandled block type: {block.type}")

    usage = response.usage
    extra = ""
    server_calls = getattr(usage, "server_tool_use", None)
    if server_calls is not None:
        extra = f", web searches={getattr(server_calls, 'web_search_requests', '?')}"
    print(f"\n(tokens in={usage.input_tokens} out={usage.output_tokens}{extra})")


def _show_search_result(block) -> None:
    """A search result block's `content` is a LIST on success, an OBJECT on error.

    Server-tool failures come back as HTTP 200 with an error object in here --
    they do *not* raise. Branch on the shape before indexing.
    """
    content = block.content
    if not isinstance(content, list):
        print(f"  !! search failed: {getattr(content, 'error_code', content)}")
        return

    print(f"  << web_search_tool_result: {len(content)} result(s)")
    for item in content:
        print(f"     - {item.title}")
        print(f"       {item.url}")


def _show_citations(block) -> None:
    for citation in getattr(block, "citations", None) or []:
        title = getattr(citation, "title", None) or getattr(citation, "url", "")
        print(f"     [cited] {title}")
