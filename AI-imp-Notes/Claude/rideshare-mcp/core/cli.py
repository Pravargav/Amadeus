"""The REPL and the streaming renderer."""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

from core.cli_chat import CliChat
from core.ui import DIM, RESET, render_tool_call


class CliApp:
    def __init__(self, agent: CliChat):
        self.agent = agent
        self.history = InMemoryHistory()
        self.session = PromptSession(
            history=self.history,
            style=Style.from_dict(
                {
                    "prompt": "#aaaaaa",
                    "completion-menu.completion": "bg:#222222 #ffffff",
                    "completion-menu.completion.current": "bg:#444444 #ffffff",
                }
            ),
            complete_while_typing=True,
            # Completion runs off the event loop so typing never blocks MCP I/O.
            complete_in_thread=True,
        )

    async def initialize(self):
        """Discover prompts and resources so they can be tab-completed.

        This is the client asking `prompts/list` and `resources/list` at
        startup -- the discovery half of MCP that mirrors `tools/list`.
        """
        words = []
        try:
            prompts = await self.agent.list_prompts()
            words += [f"/{p.name}" for p in prompts]
            print(f"{DIM}prompts:{RESET} " + ", ".join(f"/{p.name}" for p in prompts))
        except Exception as exc:
            print(f"{DIM}(no prompts: {exc}){RESET}")

        try:
            resources = await self.agent.doc_client.list_resources()
            words += ["@" + str(r.uri).replace("rideshare://", "") for r in resources]
            print(
                f"{DIM}resources:{RESET} "
                + ", ".join("@" + str(r.uri).replace("rideshare://", "") for r in resources)
            )
        except Exception as exc:
            print(f"{DIM}(no resources: {exc}){RESET}")

        self.session.completer = WordCompleter(words, sentence=True)
        print(f"{DIM}Ctrl-C to quit.{RESET}\n")

    async def run(self):
        while True:
            try:
                user_input = await self.session.prompt_async("> ")
                if not user_input.strip():
                    continue

                print()

                # Per-turn state for the stream renderer. Keyed by content
                # block index, because tool arguments arrive interleaved.
                tool_calls: dict[int, dict] = {}

                async def handle_event(event):
                    etype = getattr(event, "type", None)

                    if etype == "content_block_start":
                        block = getattr(event, "content_block", None)
                        if getattr(block, "type", None) == "tool_use":
                            print()
                            tool_calls[event.index] = {
                                "name": block.name,
                                "args": "",
                            }

                    elif etype == "content_block_delta":
                        delta = getattr(event, "delta", None)
                        dtype = getattr(delta, "type", None)

                        if dtype == "text_delta":
                            # Print tokens as they arrive.
                            print(delta.text, end="", flush=True)

                        elif dtype == "input_json_delta":
                            # Tool arguments stream as JSON *fragments*; they
                            # are unparseable until the block ends, so buffer.
                            entry = tool_calls.setdefault(
                                event.index, {"name": "", "args": ""}
                            )
                            entry["args"] += delta.partial_json

                    elif etype == "content_block_stop":
                        entry = tool_calls.pop(event.index, None)
                        if entry and entry["name"]:
                            render_tool_call(entry["name"], entry["args"])

                await self.agent.run(
                    user_input, stream=True, on_event=handle_event
                )

                print("\n")

            except KeyboardInterrupt:
                print("\nbye.")
                break
            except EOFError:
                break
            except Exception as exc:
                print(f"\n  error: {exc}\n")
