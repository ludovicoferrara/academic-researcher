from typing import Annotated
from langchain_core.tools import tool

@tool
def print_string(
    text: Annotated[str, "The output to print"]
) -> str:
    """
    Use this to print the result.
    """
    print(text)
    return f"The string has been printed. Respond with FINAL ANSWER."
