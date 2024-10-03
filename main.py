import functools
import getpass
import os

from langchain_cohere import ChatCohere
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)

from langchain_openai import OpenAI

from graph_elements.agent_node import AgentNodeFactory
from graph_elements.agent_state import AgentState


from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import END, StateGraph, START

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

import operator
from typing import Annotated, Sequence, TypedDict

from tools.arXiv_research import arxiv_search
from tools.python_repl import python_repl

from langchain_core.messages import AIMessage

from langgraph.prebuilt import ToolNode

from typing import Literal

from IPython.display import Image, display

from graph_elements.agent import Agent
from graph_elements.router import Router
from tools.arXiv_research import arxiv_search 
from tools.printer import print_string

#os.environ["TAVILY_API_KEY"] = "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"
#os.environ["OPENAI_API_KEY"] = "sk-GEB9oAjwKUnuCxlEO6gu8GzO1D75F4WLxo6UhPkz4HT3BlbkFJVjxNR2lUFVB1wSm_4annlkQb4wnEhqK04auNR0bfwA"
os.environ["COHERE_API_KEY"] = "LWd3Z734C3sOyWTPFYIxk1L7GAIJU2BTSC7F9h17"

#def _set_if_undefined(var: str):
 #   if not os.environ.get(var):
  #      os.environ[var] = getpass.getpass(f"Please provide your {var}")

#hf_llm = HuggingFaceHub(
  #  repo_id="OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",  # Modello open source gratuito e pubblico
 #   huggingfacehub_api_token="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"
#)
#llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7)

llm = ChatCohere(cohere_api_key="LWd3Z734C3sOyWTPFYIxk1L7GAIJU2BTSC7F9h17")

#_set_if_undefined("TAVILY_API_KEY")

#tavily_tool = TavilySearchResults(max_results=5)

# Warning: This executes code locally, which can be unsafe when not sandboxed
#repl = PythonREPL()

state = AgentState(
    messages=[],
    sender=""
)

# Creazione e Definizione degli agenti
#research_agent = Agent(
   # hf_llm,
  #  [tavily_tool],
 #   system_message="You should provide accurate data for the chart_generator to use.",
#)
#research_node = AgentNode(state=state, agent=research_agent, name="Researcher")

#chart_agent = Agent(
   # hf_llm,
  #  [python_repl],
 #   system_message="Any charts you display will be visible by the user.",
#)
#chart_node = AgentNode(state=state, agent=chart_agent, name="chart_generator")

arXiv_agent = Agent(
    llm,
    [arxiv_search],
    system_message="You should provide titles, authors and abstracts based on the search term.",
)
arXiv_node = functools.partial(AgentNodeFactory.agent_node, agent=arXiv_agent.agent, name="arXiv_researcher")

printer_agent = Agent(
    llm,
    [print_string],
    system_message="Any string you print is visible to the user.",
)
printer_node = functools.partial(AgentNodeFactory.agent_node, agent=printer_agent.agent, name="printer_researcher")

tools = [arxiv_search, print_string]
tool_node = ToolNode(tools)

workflow = StateGraph(AgentState)

workflow.add_node("arXiv_researcher", arXiv_node)
workflow.add_node("printer", printer_node)

#workflow.add_node("chart_generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "arXiv_researcher",
    Router.route,
    {"continue": "printer", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "printer",
    Router.route,
    {"continue": "arXiv_researcher", "call_tool": "call_tool", "__end__": END},
)

workflow.add_conditional_edges(
    "call_tool",
    lambda x: x["sender"],
    {
        "arXiv_researcher": "arXiv_researcher",
        "printer": "printer",
    },
)
workflow.add_edge(START, "arXiv_researcher")
graph = workflow.compile()

print("Graph definition done")
input("press any key to continue")

try:
   display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
except Exception:
   pass

print("Graph display done")
input("press any key to continue")

events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Research articles about artificial intelligence"
            )
        ],
    },
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")
