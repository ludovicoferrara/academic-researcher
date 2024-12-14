from typing import Annotated
from langchain_core.tools import tool
from bs4 import BeautifulSoup
import json

@tool
def parse_arxiv_data(
    xml_data: Annotated[str, "The XML files obtained through arXiv."]
):
    """
    Parse the articles and format them to JSON.
    """
    entries_list = []  # Inizializza sempre la variabile

    try:
        # Parsing con BeautifulSoup
        soup = BeautifulSoup(xml_data, 'lxml-xml')

        # Set per tenere traccia degli ID già visti
        seen_ids = set()

        # Iterare sui risultati e stampare informazioni utili
        entries = soup.find_all('entry')
        if not entries:
            raise ValueError("No entries found in the XML data")

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

            entry_data = {
                "id": id,
                "title": title,
                "authors": author_names,
                "abstract": summary
            }

            # Append the entry to the list
            entries_list.append(entry_data)

    except Exception as e:
        print(f"Errore nel parsing: {e}")

    # Converte l'elenco in formato JSON
    output_json = json.dumps(entries_list, indent=4)

    return f"The following articles have been parsed:\n\n{output_json}\n\nRespond with FINAL ANSWER only if this is the result for the last search term."
