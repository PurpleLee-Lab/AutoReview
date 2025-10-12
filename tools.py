def tool_1() -> str:
    return "This is a tool"


ALL_TOOLS = {
    "tool_1": {
        "meta": {
            "type": "function",
            "function": {
                "name": "tool_1",
                "description": "A simple tool that returns a string.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        "func": tool_1
    }
}
