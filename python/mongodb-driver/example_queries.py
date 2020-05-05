#!python3

import pymongo
from pymongo import MongoClient
from tabulate import tabulate

EARTH_RADIUS = 6371.0
MDB_URL = "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19"


def main():
    client = MongoClient(MDB_URL)
    db = client.get_database("covid19")
    stats = db.get_collection("global_and_us")
    metadata = db.get_collection("metadata")

    # Get some results for the UK:
    print("\nMost recent 10 global_and_us for the UK:")
    results = (
        stats.find({"country": "United Kingdom", "state": None})
        .sort("date", pymongo.DESCENDING)
        .limit(10)
    )
    print_table(["date", "confirmed", "deaths"], results)

    # Get the last date loaded:
    meta = metadata.find_one()
    last_date = meta["last_date"]

    # Show the 5 locations with the most recovered cases:
    print("\nThe last day's highest reported recoveries:")
    results = (
        stats.find({"date": last_date}).sort("recovered", pymongo.DESCENDING).limit(5)
    )
    print_table(["combined_name", "recovered"], results)

    # Confirmed cases for all countries within 500km of Paris:
    print(
        "\nThe last day's confirmed cases for all the countries within 500km of Paris:"
    )
    results = stats.find(
        {
            "date": last_date,
            "loc": {
                "$geoWithin": {
                    "$centerSphere": [[2.341908, 48.860199], 500.0 / EARTH_RADIUS]
                }
            },
        }
    )
    print_table(["combined_name", "confirmed"], results)


def print_table(doc_keys, search_results, headers=None):
    """
    Utility function to print a query result as a table.

    Params:
        doc_keys: A list of keys for data to be extracted from each document.
        search_results: A MongoDB cursor.
        headers: A list of headers for the table. If not provided, attempts to
            generate something sensible from the provided `doc_keys`
    """
    if headers is None:
        headers = [key.replace("_", " ").replace("-", " ").title() for key in doc_keys]
    records = (extract_tuple(doc, doc_keys) for doc in search_results)
    print(tabulate(records, headers=headers))


def extract_tuple(mapping, keys):
    """
    Extract a tuple from a mapping by requesting a sequence of keys.
    
    Missing keys will result in `None` values in the resulting tuple.
    """
    return tuple([mapping.get(key) for key in keys])


if __name__ == "__main__":
    main()
