"""
tools.py - two fake "shop" tools: the SCHEMA Claude sees, and the PYTHON that runs.

Remember the split:
  * the schema  = what you send to the API  (name, description, input_schema)
  * the function = what YOUR code runs locally. The API never runs it for you.
"""

# ---------- 1. Schemas: what Claude sees in the `tools` parameter ----------

get_price_schema = {
    "name": "get_price",
    "description": "Get the price in USD of a product in our shop.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product": {"type": "string", "description": "Product name, e.g. 'laptop'"}
        },
        "required": ["product"],
    },
}

get_stock_schema = {
    "name": "get_stock",
    "description": "Get how many units of a product are currently in stock.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product": {"type": "string", "description": "Product name, e.g. 'laptop'"}
        },
        "required": ["product"],
    },
}

ALL_TOOLS = [get_price_schema, get_stock_schema]


# ---------- 2. Implementations: plain Python, no Claude involved ----------

PRICES = {"laptop": 1200, "mouse": 25, "keyboard": 75}
STOCK = {"laptop": 4, "mouse": 130, "keyboard": 0}


def get_price(product):
    return f"{product} costs ${PRICES.get(product.lower(), 'unknown')}"


def get_stock(product):
    return f"{product}: {STOCK.get(product.lower(), 0)} units in stock"


# ---------- 3. Dispatcher: name + input dict -> string result ----------

def run_tool(name, tool_input):
    """Map a tool_use block's name/input onto the real function.

    The result you return must be a STRING (or a list of blocks) - it goes
    straight into a tool_result block, so Claude reads it as text.
    """
    if name == "get_price":
        return get_price(tool_input["product"])
    if name == "get_stock":
        return get_stock(tool_input["product"])
    return f"Error: unknown tool {name}"
