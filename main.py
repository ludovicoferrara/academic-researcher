import getpass
import os

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)

from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import END, StateGraph, START

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

import operator
from typing import Annotated, Sequence, TypedDict

from langchain import HuggingFaceHub

import functools

from langchain_core.messages import AIMessage

from langgraph.prebuilt import ToolNode

from typing import Literal

from IPython.display import Image, display

from agents_creation.agent import Agent

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

print("Setup done")
input("press any key to continue")

tavily_tool = TavilySearchResults(max_results=5)

# Warning: This executes code locally, which can be unsafe when not sandboxed
repl = PythonREPL()

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )

print("Tools creation done")
input("press any key to continue")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str

print("State definition done")
input("press any key to continue")

# Helper function to invoke agent
def agent_node(state, agent : Agent, name):
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
    
    return {
        "messages": [result],
        "sender": name,
    }

# Definizione degli agenti
research_agent = Agent(
    hf_llm,
    [tavily_tool],
    system_message="You should provide accurate data for the chart_generator to use.",
)
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

chart_agent = Agent(
    hf_llm,
    [python_repl],
    system_message="Any charts you display will be visible by the user.",
)
chart_node = functools.partial(agent_node, agent=chart_agent, name="chart_generator")

print("Agent definition done")
input("press any key to continue")

tools = [tavily_tool, python_repl]
tool_node = ToolNode(tools)

print("Tool node definition done")
input("press any key to continue")

def router(state) -> Literal["call_tool", "__end__", "continue"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        return "__end__"
    return "continue"

print("Edge logic definition done")
input("press any key to continue")

workflow = StateGraph(AgentState)

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
                content="Fetch the UK's GDP over the past 5 years,"
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
