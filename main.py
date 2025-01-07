import functools
import os

from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

from langchain_openai import ChatOpenAI

from langchain_core.messages import (
    HumanMessage
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
from tools.term_generation import generate_terms


def main(): 
    api_key = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(model="gpt-4o", api_key=api_key)

    search_term_agent = Agent(
        llm,
        [generate_terms],
        system_message="You should generate alternative search terms."
    )
    search_term_node = functools.partial(AgentNodeFactory.agent_node, agent=search_term_agent.agent, name="term_generator")

    arXiv_agent = Agent(
        llm,
        [arxiv_search],
        system_message="You should make a research on arXive and provide Ids, titles, authors and abstracts. Dont't parse the XML file, another agent will do that."
    )
    arXiv_node = functools.partial(AgentNodeFactory.agent_node, agent=arXiv_agent.agent, name="arXiv_search")

    parser_agent = Agent(
        llm,
        [parse_arxiv_data],
        system_message="You should parse the XML files obtained through arXiv search."
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
    
    humanPrompt = "I want you to search articles that talk about Quantum Mechanics."

    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    content=
                    f"You are given this prompt: {humanPrompt}\n "
                    " Generate 3 alternative short search terms related to the prompt, "
                    " use the terms to search articles about that on arXiv, "
                    " and after that, parse the obtained files. "
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