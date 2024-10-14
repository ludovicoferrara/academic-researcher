from typing import Annotated
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import re

def extract_prompts(input_string):
    return re.findall(r'"(.*?)"', input_string)


@tool
def arxiv_search(
    search_terms: Annotated[str, "the search terms in JSON format to make research on arXiv"],
    start: int = 0,
    max_results: int = 10
) -> str:
    """
    Use this tool to make multiple researches of articles on arXiv. It returns titles, authors and abstracts.
    """
    first_term= extract_prompts(search_terms)[0]
    second_term= extract_prompts(search_terms)[1]

    first_xml_data = fetch_arxiv_data(first_term, start, max_results)
    second_xml_data = fetch_arxiv_data(second_term, start, max_results)
    #TODO Join xml data
    if first_xml_data:
        return parse_arxiv_data(first_xml_data) 
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
        # Imposta un timeout di 10 secondi
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

# Funzione per parsare i risultati XML con BeautifulSoup
from bs4 import BeautifulSoup

def parse_arxiv_data(xml_data):
    # Parsing con BeautifulSoup
    soup = BeautifulSoup(xml_data, 'lxml-xml')
    
    # Set per tenere traccia degli ID già visti
    seen_ids = set()
    
    # Iterare sui risultati e stampare informazioni utili
    entries = soup.find_all('entry')
    s = ""
    for entry in entries:
        id = entry.find('id').text
        
        # Verifica se l'ID è già stato elaborato
        if id in seen_ids:
            continue  # Salta se l'ID è già stato processato
        
        # Aggiungi l'ID al set
        seen_ids.add(id)
        
        title = entry.find('title').text
        summary = entry.find('summary').text
        authors = entry.find_all('author')
        author_names = [author.find('name').text for author in authors]
        author_names = ', '.join(author_names)
        
        s += f"Id: {id} Title: {title} Authors: {author_names} Abstract: {summary}" + ("-" * 40)
    
    return s


# Esempio di utilizzo
#search_term = "quantum computing"
#xml_data = fetch_arxiv_data(search_term)

#if xml_data:
#    parse_arxiv_data(xml_data)
