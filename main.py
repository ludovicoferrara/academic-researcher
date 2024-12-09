import functools
import os

#from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

from langchain_openai import ChatOpenAI
#from langchain_cohere import ChatCohere

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
#from tools.python_repl import python_repl
from tools.term_generation import generate_terms


def main(): 
    api_key = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(model="gpt-4o", api_key=api_key)

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
        system_message="You should parse and format to json the files obtained through arXiv search."
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
    # Define the initial state
    # initial_state = {
    #     "messages": [
    #         HumanMessage(
    #             content="Generate an alternative search term to Retrieval Augmented Generation. "
    #                     "Use that term to search articles about that on arXiv. Then parse the articles that arXiv returns. "
    #                     "Do all the precedent steps 3 times."
    #         )
    #     ],
    # }
    # recursion_limit = 150
    # final_state = graph.invoke(initial_state)

    #display(
    #    Image(
    #        graph.get_graph().draw_mermaid_png(
    #            draw_method=MermaidDrawMethod.API,
    #        )
    #    )
    #)
    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="Generate 3 alternative short search terms related to Quantum Computing. "
                    " Use the terms to search articles about that on arXiv. "
                    " Then parse the obtained xml files and format them to json. "
                )
            ],
        },
        {"recursion_limit": 150},
    )
    for s in events:
        print(s)
        print("----\n")


if __name__ == "__main__":
    main()