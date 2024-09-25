from agents_creation.agent import Agent

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

class AgentNode : 

    def __init__(self, state, agent : Agent, name): 
        prompt : ChatPromptTemplate = agent.prompt
        llm = agent.llm
    
        # Concatenare i contenuti dei messaggi in una singola stringa
        messages = state["messages"]
        prompt_text = "\n".join([message.content for message in messages])
    
        # Passare il prompt al modello LLM  
        response = llm(prompt_text)
    
        # Verifica se la risposta è una stringa o un dizionario
        if isinstance(response, str):
            result_content = response  # Se è una stringa, usala direttamente
        else:
            # In caso di altre strutture, gestiscile qui (es. se il modello restituisce un dizionario)
            result_content = response.get("content", "Errore: risposta inattesa dal modello.")

        # Creiamo il formato corretto per il messaggio di ritorno
        result = AIMessage(content=result_content, name=name)
    
        self.messages = result,
        self.sender = name,