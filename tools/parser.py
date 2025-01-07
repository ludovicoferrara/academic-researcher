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
    entries_list = [] 
    try:
        soup = BeautifulSoup(xml_data, 'lxml-xml')

        seen_ids = set()

        entries = soup.find_all('entry')
        if not entries:
            raise ValueError("No entries found in the XML data")

        for entry in entries:
            id = entry.find('id').text

            if id in seen_ids:
                continue 

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

            entries_list.append(entry_data)

    except Exception as e:
        print(f"Errore nel parsing: {e}")

    output_json = json.dumps(entries_list, indent=4)

    return f"The following articles have been parsed:\n\n{output_json}\n\nRespond with FINAL ANSWER only if this is the result for the last search term."
