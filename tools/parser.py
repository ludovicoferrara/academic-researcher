from typing import Annotated
from langchain_core.tools import tool
from bs4 import BeautifulSoup
import json

@tool
def parse_arxiv_data(
    xml_data: Annotated[str, "The xml file obtained through arXiv."]
    ):
    """
     Use this to parse the articles and format them to json.
    """
    # Parsing con BeautifulSoup
    soup = BeautifulSoup(xml_data, 'lxml-xml')
    
    # Set per tenere traccia degli ID già visti
    seen_ids = set()
    entries_list=[]
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
        
        entry_data = {
        "id": entry.find('id').text,
        "title": title,
        "authors": author_names,
        "abstract": summary
        }
    
        # Append the entry to the list
        entries_list.append(entry_data)
    
        #s += f"Id: {id} Title: {title} Authors: {author_names} Abstract: {summary}" + "\n\n"
    
    output_json = json.dumps(entries_list, indent=4)

    return f"The following articles have been parsed: \n\n\n{output_json}\n\n\n.\nRespond with FINAL ANSWER only if this is the result for the last search term."