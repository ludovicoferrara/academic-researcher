from typing import Annotated
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

@tool
def arxiv_search(
    search_term: Annotated[str, "the search tearm to make research on arXiv"],
    start: int = 0,
    max_results: int = 10
) -> str:
    """
    Use this tool to make research of articles on arXiv. It returns titles, authors and abstracts.
    """
    xml_data = fetch_arxiv_data(search_term, start, max_results)
    
    if xml_data:
        return parse_arxiv_data(xml_data) 
    else:
        return "No available data or bad request error"



# Funzione per costruire l'URL della query
def build_query_url(search_term, start=0, max_results=10):
    base_url = "http://export.arxiv.org/api/query"
    query = f"search_query=all:{search_term}&start={start}&max_results={max_results}"
    return f"{base_url}?{query}"

# Funzione per inviare la richiesta e ottenere i risultati
def fetch_arxiv_data(search_term, start=0, max_results=10):
    url = build_query_url(search_term, start, max_results)
    
    try:
        # Imposta un timeout di 10 secondi
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Verifica se la richiesta ha avuto successo
        return response.content
    
    except ConnectionError:
        print("Errore di connessione: impossibile connettersi all'host.")
    except Timeout:
        print("Errore di timeout: la richiesta ha impiegato troppo tempo.")
    except RequestException as e:
        print(f"Errore nella richiesta: {e}")
    return None

# Funzione per parsare i risultati XML con BeautifulSoup
def parse_arxiv_data(xml_data):
    # Parsing con BeautifulSoup
    soup = BeautifulSoup(xml_data, 'lxml-xml')
    
    # Iterare sui risultati e stampare informazioni utili
    entries = soup.find_all('entry')
    s = ""
    for entry in entries:
        title = entry.find('title').text
        summary = entry.find('summary').text
        authors = entry.find_all('author')
        author_names = [author.find('name').text for author in authors]
        author_names = ', '.join(author_names)
        s+= "Title: {title}" + "Authors: {author_names}" + "Abstract: {summary}" + ("-" * 40) 
    return s

# Esempio di utilizzo
#search_term = "quantum computing"
#xml_data = fetch_arxiv_data(search_term)

#if xml_data:
#    parse_arxiv_data(xml_data)
