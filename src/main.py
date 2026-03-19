from argparse import ArgumentParser

from db import bulk_insert, init_db
from exporter import export_csv
from scraper import scrape_search

URL = "https://www.caasa.it/roma/roma/appartamento/in-affitto.html"  # example url


def cmd_scrape(args):
    """
    Execute scraping and save it in db
    """

    init_db()
    print(f"Scraping {args.url}")
    listings = scrape_search(args.url)
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

    # export subcommand
    p_export = subparsers.add_parser("export", help="export to CSV")
    p_export.add_argument(
        "--output", help="output file path"
    )  # listings.csv is the default in exporter.py

    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
