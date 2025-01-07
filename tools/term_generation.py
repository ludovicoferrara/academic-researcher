from typing import Annotated
from langchain_cohere import ChatCohere
from langchain_core.tools import tool
import os

@tool
def generate_terms(
    prompt: Annotated[str, "The prompt from which generate an alternative search term"]
) -> str:
    """
    This tool generates an alternative search term based on the given prompt
    using the same Cohere LLM instance.
    """
    api_key = os.getenv("COHERE_API_KEY")

    llm = ChatCohere(cohere_api_key=api_key)
    
    generation_prompt = f"Given the prompt: {prompt}, respond with a different alternative search term"    
    response = llm.invoke(generation_prompt)
    
    return response.content
