import re
import string
import time

import requests
from bs4 import BeautifulSoup

REQUESTS_DELAY = 2.0
MAX_PAGES = 1

KEY_VALUE_FIELDS = {"floor": "piano", "bathrooms": "bagni"}

BOOLEAN_FLAGS = {
    "con terrazza",
    "con balcone",
    "arredato",
    "cantina",
    "posto auto",
    "con giardino",
    "con box",
    "acensore",
}


def __get_span_text(span) -> str:
    icon = span.find("i")
    if icon and icon.get("title"):
        return icon["title"].strip()
    bold = span.find("b")
    if bold and bold.get("title"):
        return bold["title"].strip()
    return span.get_text(separator=" ", strip=True)


def __parse_detail_text(text: str) -> tuple | None:
    text_lower = text.lower()
    ce_match = re.match(r"classe energetica\s+(.+)", text_lower)
    if ce_match:
        return ("classe energetica", text.split()[-1])
    for prefix, key in KEY_VALUE_FIELDS.items():
        if text_lower.startswith(prefix + ":"):
            value = text[len(prefix) + 1 :].strip()
            return (key, value)
    if text_lower in BOOLEAN_FLAGS:
        return (__sanitize_key(text_lower), True)
    return ("extra_" + __sanitize_key(text_lower), True)


def parse_details(card) -> dict:
    details = {}
    details_div = card.find("div", class_="result-item__details")
    if not details_div:
        return details
    for span in details_div.find_all("span"):
        raw_text = __get_span_text(span)
        if not raw_text:
            continue
        result = __parse_detail_text(raw_text)
        if result:
            key, value = result
            details[key] = value
    return details


def fetch_page(url):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()  # launch exception on 4xx/5xx
        return BeautifulSoup(res.text, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def __sanitize_key(text: str) -> str:
    """
    Return a sanitized key for SQLite queries
    """
    allowed = string.ascii_lowercase + string.digits
    key = text.lower().strip()
    # map any invalid characters to underscores
    table = str.maketrans({c: "_" for c in key if c not in allowed})
    key = key.translate(table).strip("_")
    return key if key else "unknown"


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

    return {"title": safe_text(".result-item__title"), **parse_details(card)}


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
