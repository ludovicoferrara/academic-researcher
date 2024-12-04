import functools
import os

from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere

from langchain_core.messages import (
    HumanMessage,
)

from graph_elements.agent_node import AgentNodeFactory
from graph_elements.agent_state import AgentState

from langgraph.graph import END, StateGraph, START

from tools.arXiv_research import arxiv_search

from langgraph.prebuilt import ToolNode

from graph_elements.agent import Agent
from graph_elements.router import Router
from tools.arXiv_research import arxiv_search 
from tools.parser import parse_arxiv_data
from tools.python_repl import python_repl
from tools.term_generation import generate_terms

#os.environ["OPENAI_API_KEY"] = "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"
os.environ["COHERE_API_KEY"] = "2xyJqgM6feH8cEREbBGJ7DqtcyDeCTUxWSAfwtMc"
os.environ["OPENAI_API_KEY"] = "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"


#hf_llm = HuggingFaceHub(
  #  repo_id="OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",  # Modello open source gratuito e pubblico
 #   huggingfacehub_api_token="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"
#)
#llm = OpenAI(model="gpt-3.5-turbo", temperature=0.7)

#llm = ChatCohere(cohere_api_key="2xyJqgM6feH8cEREbBGJ7DqtcyDeCTUxWSAfwtMc")
llm = ChatOpenAI(model="gpt-4o", api_key="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")

search_term_agent = Agent(
    llm,
    [generate_terms],
    system_message="You should generate an alternative search term."
)
search_term_node = functools.partial(AgentNodeFactory.agent_node, agent=search_term_agent.agent, name="term_generator")

arXiv_agent = Agent(
    llm,
    [arxiv_search],
    system_message="You should make a research on arXive and provide Ids, titles, authors and abstracts."
)
arXiv_node = functools.partial(AgentNodeFactory.agent_node, agent=arXiv_agent.agent, name="arXiv_search")

#printer_agent = Agent(
   # llm,
  #  [print_string],
 #   system_message="You should format the string is given to you by calling the proper tool according to the request." 
#    "If in the request there isn't a specification about what to show, you should call the tool that show the most information"
#)
parser_agent = Agent(
    llm,
    [parse_arxiv_data],
    system_message="You should parse the xml file obtained through arXiv search."
)
parser_node = functools.partial(AgentNodeFactory.agent_node, agent=parser_agent.agent, name="parser")

tools = [parse_arxiv_data, arxiv_search, generate_terms]
tool_node = ToolNode(tools)

workflow = StateGraph(AgentState)

workflow.add_node("term_generator", search_term_node)

workflow.add_node("arXiv_search", arXiv_node)

workflow.add_node("parser", parser_node)

workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "term_generator",
    Router.route,
    {"continue": "arXiv_search", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "arXiv_search",
    Router.route,
    {"continue": "parser", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "parser",
    Router.route,
    {"continue": "term_generator", "call_tool": "call_tool", "__end__": END},
)
workflow.add_conditional_edges(
    "call_tool",
    lambda x: x["sender"],
    {
        "term_generator": "term_generator",
        "arXiv_search": "arXiv_search",
        "parser": "parser",
    },
)
workflow.add_edge(START, "term_generator")
graph = workflow.compile()

print("Graph definition done")
input("press any key to continue")

#display(
#    Image(
#        graph.get_graph().draw_mermaid_png(
#            draw_method=MermaidDrawMethod.API,
#        )
#    )
#)
#events = graph.stream(
#    {
#        "messages": [
#            HumanMessage(
#                content="Generate one alternative search term to Retrieval Augmented Generation. "
#                "Use that term to search articles about on arXiv. Than print the abstracts of the articles that arXiv returns."
#                "Do all the precedent steps 3 times."
#            )
#        ],
#    },
#    {"recursion_limit": 150},
#)
events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Generate an alternative search term to Retrieval Augmented Generation. "
                "Use that term to search articles about that on arXiv. Than parse the articles that arXiv returns."
                "Do all the precedent steps 3 times."
            )
        ],
    },
    {"recursion_limit": 150},
)

for s in events:
    print(s)
    print("----\n")
