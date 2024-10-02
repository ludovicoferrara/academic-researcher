from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import LLM
class Agent:

    def __init__(self, llm: LLM , tools, system_message: str) :
        agent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
        agent_prompt = agent_prompt.partial(system_message = system_message)
        agent_prompt = agent_prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

        self.llm = llm
        self.prompt: ChatPromptTemplate = agent_prompt
        self.tools = tools
    