import requests
from bs4 import BeautifulSoup

def scrape_links(links):
    full_text = ""
    for link in links:
        try:
            resp = requests.get(link, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style']):
                tag.decompose()
            full_text += soup.get_text(separator=" ", strip=True)[:3000]
        except:
            continue
    return full_text
