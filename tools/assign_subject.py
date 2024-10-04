from typing import Annotated
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

@tool
def arxiv_search(
    category: Annotated[str, "the category of the topic to research on arXiv"],
) -> str:
    """
    Use this tool to assign a subject code to the prompt. It returns the code of the subject.
    """
    
    return ""

