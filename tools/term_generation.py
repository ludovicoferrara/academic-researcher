from typing import Annotated
from langchain_cohere import ChatCohere
from langchain_core.tools import tool

# Definisci il tool che utilizza l'istanza del modello LLM per generare 2 termini alternativi
@tool
def generate_terms(
    prompt: Annotated[str, "The prompt from which generate alternative search terms"]
) -> str:
    """
    This tool generates 2 alternative search terms based on the given prompt
    using the same Cohere LLM instance.
    """
    
    llm = ChatCohere(cohere_api_key="LWd3Z734C3sOyWTPFYIxk1L7GAIJU2BTSC7F9h17")
    
    generation_prompt = f"Given the prompt: {prompt}, respond with 3 different alternative search terms in the following JSON format" + "{Term1:\"first-term\", Term2:\"second-term\", Term3:\"third-term\"}."    
    response = llm.invoke(generation_prompt)
    
    return response.content
