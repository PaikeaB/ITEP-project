import requests
from bs4 import BeautifulSoup
import csv


SEARCH_QUERIES = [
    "platform governance social media law",
    "common carriage internet platforms",
    "section 230 editorial immunity",
    "net neutrality discourse",
    "content moderation legal framework",
    "platform liability common carrier"
]

def search_google_scholar(query, num_results=5):
    """
    Search Google Scholar and return basic results.
    Note: This is a basic scraper - Google may block if used extensively.
    Consider using scholarly library or manual search instead.
    """
    print(f"\nSearch query: '{query}'")
    print("Visit: https://scholar.google.com/scholar?q=" + query.replace(' ', '+'))
    print("Add results to literature_sources.csv manually")



template_rows = []


print("LITERATURE SEARCH HELPER")
print("\nSearch these queries on Google Scholar and add 5-8 sources:\n")

for query in SEARCH_QUERIES:
    search_google_scholar(query)


with open('metadata/literature_sources.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'author', 'year', 'title', 'publication', 'url',
        'main_argument', 'relevance_to_project', 'notes'
    ])
    writer.writeheader()

    writer.writerow({
        'author': 'Candeub, Adam',
        'year': '2020',
        'title': 'Bargaining for Free Speech: Common Carriage, Network Neutrality, and Section 230',
        'publication': 'Yale J.L. & Tech.',
        'url': 'https://yjolt.org/sites/default/files/bargaining_for_free_speech_22_yale_j.l._tech._391_2020.pdf',
        'main_argument': 'Network regulation operates as "regulatory bargain" - platforms get liability relief but should have anti-discrimination obligations',
        'relevance_to_project': 'Frames neutrality as negotiated political concept rather than technical property',
        'notes': 'Already reviewed - foundation for project'
    })

print("\nTemplate created: metadata/literature_sources.csv")
print("Fill in 5-8 additional sources from your searches")
