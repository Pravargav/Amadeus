"""
tools.py - SCALABLE TOOL ROUTING + THE TOOLS WE'RE ADDING

What we are replacing (part 1's router). It works, but every new tool means
editing this chain, and forgetting one branch fails silently:

    def run_tool(name, tool_input):
        if name == "get_price":
            return get_price(tool_input["product"])
        elif name == "get_stock":
            return get_stock(tool_input["product"])
        elif name == "search_products":
            ...                      # <- grows forever

The scalable version: one REGISTRY dict, name -> {schema, function}.
A tool registers itself when the file is imported, so adding a tool means
adding a function - the router never changes again.
"""

# ---------------------------------------------------------------
# THE REGISTRY  (name -> {"schema": ..., "fn": ...})
# ---------------------------------------------------------------

TOOL_REGISTRY = {}


def tool(schema):
    """Decorator: register a Python function together with its JSON schema."""
    def decorator(fn):
        TOOL_REGISTRY[schema["name"]] = {"schema": schema, "fn": fn}
        return fn
    return decorator


# ---------------------------------------------------------------
# THE TOOLS WE'RE ADDING  (fake data - this project is about the plumbing)
# ---------------------------------------------------------------

PRODUCTS = {
    "laptop":   {"price": 1200, "stock": 4},
    "mouse":    {"price": 25,   "stock": 130},
    "keyboard": {"price": 75,   "stock": 0},
}


@tool({
    "name": "search_products",
    "description": "List the products we sell whose name matches a keyword.",
    "input_schema": {
        "type": "object",
        "properties": {"keyword": {"type": "string", "description": "e.g. 'key'"}},
        "required": ["keyword"],
    },
})
def search_products(keyword):
    hits = [p for p in PRODUCTS if keyword.lower() in p]
    return ", ".join(hits) if hits else "no matching products"


@tool({
    "name": "get_price",
    "description": "Get the price in USD of one product.",
    "input_schema": {
        "type": "object",
        "properties": {"product": {"type": "string"}},
        "required": ["product"],
    },
})
def get_price(product):
    # Raising is fine - the router turns exceptions into is_error tool_results.
    return f"{product} costs ${PRODUCTS[product.lower()]['price']}"


@tool({
    "name": "get_stock",
    "description": "Get how many units of one product are in stock.",
    "input_schema": {
        "type": "object",
        "properties": {"product": {"type": "string"}},
        "required": ["product"],
    },
})
def get_stock(product):
    return f"{product}: {PRODUCTS[product.lower()]['stock']} units in stock"


@tool({
    "name": "place_order",
    "description": "Order more units of a product from the supplier.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product": {"type": "string"},
            "quantity": {"type": "integer", "description": "Units to order"},
        },
        "required": ["product", "quantity"],
    },
})
def place_order(product, quantity):
    return f"ordered {quantity} x {product} - arrives in 3 days"


# ---------------------------------------------------------------
# ADDING TOOLS TO THE CONVERSATION
#   Build the `tools` parameter straight from the registry, so the
#   list Claude sees can never drift from the code that runs.
# ---------------------------------------------------------------

ALL_TOOLS = [entry["schema"] for entry in TOOL_REGISTRY.values()]


# ---------------------------------------------------------------
# THE TOOL ROUTER  (+ ERROR HANDLING)
# ---------------------------------------------------------------

def run_tool(name, tool_input):
    """Look the tool up and call it. Returns a string, never raises.

    `tool_input` is already a dict, so **tool_input maps the keys in the
    schema straight onto the function's parameters. Name them the same and
    the router stays generic.
    """
    entry = TOOL_REGISTRY.get(name)
    if entry is None:
        return f"Error: no such tool '{name}'"
    try:
        return str(entry["fn"](**tool_input))
    except Exception as e:
        return f"Error running {name}: {type(e).__name__}: {e}"


def run_tool_block(block):
    """tool_use block -> tool_result block. The whole handoff, one function."""
    output = run_tool(block.name, block.input)
    return {
        "type": "tool_result",
        "tool_use_id": block.id,            
        "content": output,
        "is_error": output.startswith("Error"),  
    }
