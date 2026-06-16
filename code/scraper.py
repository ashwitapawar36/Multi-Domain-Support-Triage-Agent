import requests
from bs4 import BeautifulSoup
import os

SOURCES = {
    "HackerRank": "https://support.hackerrank.com/hc/en-us",
    "Claude":     "https://support.claude.com/en/",
    "Visa":       "https://www.visa.co.in/support.html",
}

CORPUS_DIR = "../corpus"

def scrape_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"  [scraper] Failed {url}: {e}")
        return ""

def build_corpus():
    os.makedirs(CORPUS_DIR, exist_ok=True)
    corpus = {}
    for company, url in SOURCES.items():
        print(f"Scraping {company} ({url})...")
        text = scrape_page(url)
        path = os.path.join(CORPUS_DIR, f"{company}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        corpus[company] = text
        print(f"  saved {len(text)} chars")
    return corpus

def load_corpus():
    corpus = {}
    for company in SOURCES:
        path = os.path.join(CORPUS_DIR, f"{company}.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                corpus[company] = f.read()
    return corpus