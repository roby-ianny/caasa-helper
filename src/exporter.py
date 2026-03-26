import csv

from db import get_connection, init_db


def export_csv(output_path: str = "listings.csv"):
    """
    Exports all the listings to a CSV file, or a custom subset if a query is provided.
    """

    init_db()
    sql = "SELECT * FROM listings ORDER BY id ASC"

    # Execute query on db
    with get_connection() as conn:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()  # get all the db rows
        columns = [
            desc[0] for desc in cursor.description
        ]  # get all the db column names

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"CSV file exported to {output_path} with a total of {len(rows)} rows.")
