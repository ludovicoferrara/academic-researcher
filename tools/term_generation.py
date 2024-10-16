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
    
    # Usa l'istanza del modello LLM di Cohere già definita
    llm = ChatCohere(cohere_api_key="LWd3Z734C3sOyWTPFYIxk1L7GAIJU2BTSC7F9h17")
    
    # Prompt per generare i termini alternativi
    generation_prompt = f"Given the prompt: {prompt}. You should respond with 3 different alternative search terms in the following "
    "JSON format {Term1:\"first-term\", Term:\"second-term\", Term3:\"third-term\"} and nothing else."    
    # Chiamata all'LLM per generare i termini alternativi
    response = llm.invoke(generation_prompt)
    
    return response.content  # Restituisce i termini generati

