from typing import Literal

class Router:
    def route(state) -> Literal["call_tool", "__end__", "continue"]:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
             return "call_tool"
        if "FINAL ANSWER" in last_message.content:
             return "__end__"
        return "continue"
