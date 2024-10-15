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

#os.environ["OPENAI_API_KEY"] = "sk-GEB9oAjwKUnuCxlEO6gu8GzO1D75F4WLxo6UhPkz4HT3BlbkFJVjxNR2lUFVB1wSm_4annlkQb4wnEhqK04auNR0bfwA"
os.environ["COHERE_API_KEY"] = "LWd3Z734C3sOyWTPFYIxk1L7GAIJU2BTSC7F9h17"

#hf_llm = HuggingFaceHub(
  #  repo_id="OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",  # Modello open source gratuito e pubblico
 #   huggingfacehub_api_token="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"
#)
#llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7)

llm = ChatCohere(cohere_api_key="LWd3Z734C3sOyWTPFYIxk1L7GAIJU2BTSC7F9h17")

state = AgentState(
    messages=[],
    sender=""
)

search_term_agent = Agent(
    llm,
    [],
    system_message="You should provide 3 different alternative terms in JSON format {Prompt1:\"first-prompt\", Prompt2:\"second-prompt\", Prompt3:\"third-prompt\"} "
    "to research articles about."
)
search_term_node = functools.partial(AgentNodeFactory.agent_node, agent=search_term_agent.agent, name="term_generator")

arXiv_agent = Agent(
    llm,
    [arxiv_search],
    system_message="You should provide titles, authors and abstracts from arXiv based on the search terms."
)
arXiv_node = functools.partial(AgentNodeFactory.agent_node, agent=arXiv_agent.agent, name="arXiv_researcher")

printer_agent = Agent(
    llm,
    [print_string],
    system_message="You should format the string is given to you by calling the proper tool according to the request." 
    "If in the request there isn't a specification about what to show, you should call the tool that show the most information"
)
printer_node = functools.partial(AgentNodeFactory.agent_node, agent=printer_agent.agent, name="printer_researcher")

tools = [arxiv_search, print_string]
tool_node = ToolNode(tools)

workflow = StateGraph(AgentState)

workflow.add_node("term_generator", search_term_node)

workflow.add_node("arXiv_researcher", arXiv_node)

workflow.add_node("printer", printer_node)

workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "term_generator",
    Router.route,
    {"continue": "arXiv_researcher"},
)
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
workflow.add_edge(START, "term_generator")
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
                content="Search articles about Retrieval Augmented Generation"
            )
        ],
    },
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----\n")
