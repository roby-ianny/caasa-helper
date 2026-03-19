import time

import requests
from bs4 import BeautifulSoup

REQUESTS_DELAY = 2.0
MAX_PAGES = 1


def fetch_page(url):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()  # launch exception on 4xx/5xx
        return BeautifulSoup(res.text, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_listing(card) -> dict:
    """
    Extract data from a single listing card
    """

    def safe_text(selector):
        """
        Give the text of an element or None if not found
        """
        el = card.select_one(selector)
        return el.get_text(strip=True) if el else None

    def safe_attr(selector, attr):
        """
        Give the HTML attribute or None if not found
        """
        el = card.select_one(selector)
        return el.get(attr) if el else None

    return {"title": safe_text(".result-item__title")}


def scrape_search(search_url: str, max_pages: int = MAX_PAGES) -> list[dict]:
    """
    Get all the search results and return them as a list of dicts
    """

    results = []

    for page in range(1, max_pages + 1):
        # page format example: https://www.caasa.it/roma/roma/appartamento/in-affitto.html?page=1
        url = search_url if page == 1 else f"{search_url}?page={page}"

        soup = fetch_page(url)
        if not soup:
            break

        # Get all the listings cards
        cards = soup.select(".result-item")

        if not cards:
            print("No listing found - end of search")

        for card in cards:
            single_result = parse_listing(card)
            results.append(single_result)

        print(f" Found {len(cards)} listings on page {page}")

        # Break to not overload the server
        time.sleep(REQUESTS_DELAY)

    return results
