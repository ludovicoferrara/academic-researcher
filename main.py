import getpass
import os

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)

from graph_elements.agent_node import AgentNode
from graph_elements.agent_state import AgentState


from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import END, StateGraph, START

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

import operator
from typing import Annotated, Sequence, TypedDict

from langchain import HuggingFaceHub

from utils import python_repl

from langchain_core.messages import AIMessage

from langgraph.prebuilt import ToolNode

from typing import Literal

from IPython.display import Image, display

from graph_elements.agent import Agent

os.environ["TAVILY_API_KEY"]= "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"

def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")

# Sostituiamo con un modello gratuito pubblico, come google/flan-t5-xl
hf_llm = HuggingFaceHub(
    repo_id="OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",  # Modello open source gratuito e pubblico
    huggingfacehub_api_token="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"
)

_set_if_undefined("TAVILY_API_KEY")

tavily_tool = TavilySearchResults(max_results=5)

# Warning: This executes code locally, which can be unsafe when not sandboxed
#repl = PythonREPL()


state = AgentState(
    messages=[],
    sender=""
)

# Creazione e Definizione degli agenti
research_agent = Agent(
    hf_llm,
    [tavily_tool],
    system_message="You should provide accurate data for the chart_generator to use.",
)
research_node = AgentNode(state=state, agent=research_agent, name="Researcher")

chart_agent = Agent(
    hf_llm,
    [python_repl],
    system_message="Any charts you display will be visible by the user.",
)
chart_node = AgentNode(state=state, agent=chart_agent, name="chart_generator")

tools = [tavily_tool, python_repl]
tool_node = ToolNode(tools)

def router(state) -> Literal["call_tool", "__end__", "continue"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        return "__end__"
    return "continue"

workflow = StateGraph(state_schema=state)

workflow.add_node("Researcher", research_node)
workflow.add_node("chart_generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {"continue": "chart_generator", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "chart_generator",
    router,
    {"continue": "Researcher", "call_tool": "call_tool", "__end__": END},
)

workflow.add_conditional_edges(
    "call_tool",
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "chart_generator": "chart_generator",
    },
)
workflow.add_edge(START, "Researcher")
graph = workflow.compile()

print("Graph definition done")
input("press any key to continue")

try:
    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
except Exception:
    pass

events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Fetch the world's population increase over the past 5 years,"
                " then draw a line graph of it."
                " Once you code it up, finish."
            )
        ],
    },
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")
