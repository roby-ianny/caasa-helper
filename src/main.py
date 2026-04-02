from argparse import ArgumentParser

import typer

from db import bulk_insert, init_db
from exporter import export_csv
from scraper import scrape_search

URL = "https://www.caasa.it/roma/roma/appartamento/in-affitto.html"  # example url


def cmd_scrape(args):
    """
    Execute scraping and save it in db
    """

    init_db()
    print(f"Scraping {args.pages} pages from {args.url}")
    if args.test:
        print("TEST MODE: parsing only one card")
    listings = scrape_search(args.url, args.pages, args.test)
    inserted, duplicates = bulk_insert(listings)


def cmd_export(args):
    """
    Export to CSV
    """
    export_csv(args.output)


def main():
    parser = ArgumentParser(
        description="Caasa.it helper - gather real estate listings and save them in a SQLite DB"
    )
    subparsers = parser.add_subparsers(dest="command")

    # scrape subcommand
    p_scrape = subparsers.add_parser("scrape", help="scrape search results")
    p_scrape.add_argument("url", help="query from 'copy-link' in caasa.it")
    p_scrape.add_argument(
        "--pages", type=int, default=5, help="number of pages to scrape"
    )
    p_scrape.add_argument(
        "--test",
        help="parses only one card",
        action="store_true",
    )

    # export subcommand
    p_export = subparsers.add_parser("export", help="export to CSV")
    p_export.add_argument(
        "--output", default="listings.csv", help="output file path"
    )  # listings.csv is the default in exporter.py

    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    typer.run(main)
