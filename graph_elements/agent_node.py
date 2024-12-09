#from cohere import ToolMessage
from graph_elements.agent import Agent
from graph_elements.agent_state import AgentState

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate


class AgentNodeFactory : 

    # Helper function to create a node for a given agent
    def agent_node(state, agent, name):
        result = agent.invoke(state)
        # We convert the agent output into a format that is suitable to append to the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        return {
            "messages": [result],
            # Since we have a strict workflow, we can
            # track the sender so we know who to pass to next.
            "sender": name,
    }
