from typing import Annotated
from langchain_core.tools import tool
import requests
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

@tool
def arxiv_search(
    search_term: Annotated[str, "the search term to make research on arXiv"],
    start: int = 0,
    max_results: int = 10
) -> str:
    """
    Use this tool to search of articles on arXiv.
    """
    xml_data = fetch_arxiv_data(search_term, start, max_results)
    if xml_data:
        return xml_data 
    else:
        return "No available data or bad request error"



# Funzione per costruire l'URL della query
def build_query_url(search_term, start=0, max_results=10):
    base_url = "https://export.arxiv.org/api/query"
    query = f"search_query=all:{search_term}&start={start}&max_results={max_results}"
    return f"{base_url}?{query}"

# Funzione per inviare la richiesta e ottenere i risultati
def fetch_arxiv_data(search_term, start=0, max_results=10):
    url = build_query_url(search_term, start, max_results)
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Verifica se la richiesta ha avuto successo
        return response.content
    
    except ConnectionError:
        print("Errore di connessione: impossibile connettersi all'host.")
    except Timeout:
        print("Errore di timeout: la richiesta ha impiegato troppo tempo.")
    except RequestException as e:
        print(f"Errore nella richiesta: {e}")
    return None