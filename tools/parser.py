# from typing import Annotated
# from langchain_core.tools import tool

# @tool
# def print_string(
#     text: Annotated[str, "The articles obtained through arXiv."]
# ) -> str:
#     """
#     Use this to format the articles.
#     """


#         title = entry.find('title').text
#         summary = entry.find('summary').text
#         authors = entry.find_all('author')
#         author_names = [author.find('name').text for author in authors]
#         author_names = ', '.join(author_names)
        
#         s += f"Id: {id} Title: {title} Authors: {author_names} Abstract: {summary}" + "\n\n"
    
#     return f"The string following string has been printed: \n\n\n{text}\n\n\n.\nRespond with FINAL ANSWER only if this is the result printed for the last search term."
from typing import Annotated
from langchain_core.tools import tool
from bs4 import BeautifulSoup

@tool
def parse_arxiv_data(
    xml_data: Annotated[str, "The xml file obtained through arXiv."]
    ):
    """
     Use this to parse the articles.
    """
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
        s+=entry.text
        title = entry.find('title').text
        summary = entry.find('summary').text
        authors = entry.find_all('author')
        author_names = [author.find('name').text for author in authors]
        author_names = ', '.join(author_names)
        
        s += f"Id: {id} Title: {title} Authors: {author_names} Abstract: {summary}" + "\n\n"
    
    return f"The following articles have been parsed: \n\n\n{s}\n\n\n.\nRespond with FINAL ANSWER only if this is the result for the last search term."