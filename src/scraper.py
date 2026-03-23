import time
from re import search

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing_extensions import List

REQUESTS_DELAY = 2.0
MAX_PAGES = 1

BOOLEAN_FEATURES = {
    "con terrazza": "terrazza",
    "con giardino": "giardino",
    "con balcone": "balcone",
    "arredato": "arredato",
    "posto auto": "posto_auto",
    "cantina": "cantina",
}


def fetch_page(url):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()  # launch exception on 4xx/5xx
        return BeautifulSoup(res.text, "lxml")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_listing(card: Tag) -> dict:
    """
    Extract data from a single listing card
    """

    def safe_text(selector: str):
        """
        Give the text of an element or None if not found
        """
        el = card.select_one(selector)
        return el.get_text(strip=True) if el else None

    def __parse_item_details(card: Tag) -> List:
        """
        Parse the .result-item__details element to extract the details of a listing
        """
        details = []
        for item in card.select_one(".result-item__details").select("span"):
            if item.find("i"):
                details.append(item.find("i").get("title"))
            elif item.find("b"):
                details.append(item.find("b").get("title"))
            else:
                details.append(item.get_text(strip=True))

        return details

    def get_features(details: Tag) -> dict:
        features_list = __parse_item_details(details)

        details_dict = {}

        for feature in features_list:
            if search(r"bagni:\s*(\d+)", feature):
                details_dict.update(
                    {"bathrooms": int(search(r"bagni:\s*(\d+)", feature).group(1))}
                )
            elif search(r"piano:\s*(\d+)", feature):
                details_dict.update(
                    {"floor": search(r"piano:\s*(\d+)", feature).group(1)}
                )
            else:
                if feature in BOOLEAN_FEATURES.keys():
                    details_dict.update({BOOLEAN_FEATURES.get(feature): True})

        return details_dict

    return {
        "title": safe_text(".result-item__title"),
        # append other details got from get_details
        **get_features(card),
        # TODO:
        # **get_price_info, # tag:
        # **get_address,
        # **get_link,
    }


def scrape_search(
    search_url: str, max_pages: int = MAX_PAGES, testMode: bool = False
) -> list[dict]:
    """
    Get all the search results and return them as a list of dicts
    """

    if testMode:
        max_pages = 1

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
            break

        if testMode:
            cards = cards[:1]
            results.append(parse_listing(cards[0]))
            break
        else:
            for card in cards:
                single_result = parse_listing(card)
                results.append(single_result)

        print(f" Found {len(cards)} listings on page {page}")

        # Break to not overload the server
        time.sleep(REQUESTS_DELAY)

    return results
