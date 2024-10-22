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
    return f"The string following string has been printed: \n\n\n{text}\n\n\n.\nIf all the results have been printed, respond with FINAL ANSWER."
