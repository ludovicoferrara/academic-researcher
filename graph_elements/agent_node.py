from cohere import ToolMessage
from graph_elements.agent import Agent
from graph_elements.agent_state import AgentState

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate


class AgentNodeFactory : 

    def agent_node(state, agent, name):
        result = agent.invoke(state)
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        return {
            "messages": [result],
            "sender": name,
    }
