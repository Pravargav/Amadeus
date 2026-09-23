"""Guards the seam between the two halves. No API key needed.

    python test_contract.py

Hand-written schemas can drift away from the functions they describe, and
nothing in the SDK or the API will tell you -- you find out when Claude sends a
well-formed tool_use that your code cannot service. If you keep hand-written
schemas, keep a test like this too.

(The @beta_tool path in agent_runner.py doesn't need any of this: the schema is
generated from the signature, so it cannot disagree with it.)
"""

import inspect
import sys

import tool_functions
import tool_schemas

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


for schema in tool_schemas.ALL:
    name = schema["name"]

    fn = tool_functions.REGISTRY.get(name)
    check(fn is not None, f"{name}: in tool_schemas.ALL but not in REGISTRY")
    if fn is None:
        continue

    sig = inspect.signature(fn)
    params = sig.parameters
    declared = set(schema["input_schema"]["properties"])
    actual = set(params)

    check(
        declared <= actual,
        f"{name}: schema declares {sorted(declared - actual)}, not in the signature",
    )

    required_by_fn = {
        p for p, v in params.items() if v.default is inspect.Parameter.empty
    }
    check(
        required_by_fn <= declared,
        f"{name}: function requires {sorted(required_by_fn - declared)}, absent from schema",
    )

    required_by_schema = set(schema["input_schema"].get("required", []))
    check(
        required_by_schema == required_by_fn,
        f"{name}: schema requires {sorted(required_by_schema)}, "
        f"function requires {sorted(required_by_fn)}",
    )

    if schema.get("strict"):
        check(
            schema["input_schema"].get("additionalProperties") is False,
            f"{name}: strict:true requires additionalProperties:false",
        )
        check(
            "required" in schema["input_schema"],
            f"{name}: strict:true requires a `required` list",
        )

orphans = set(tool_functions.REGISTRY) - {s["name"] for s in tool_schemas.ALL}
check(not orphans, f"in REGISTRY but never published to Claude: {sorted(orphans)}")


if failures:
    print("CONTRACT VIOLATIONS:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)

print(f"ok - {len(tool_schemas.ALL)} tools, schemas and functions agree")
