#!python3

import pymongo
from pymongo import MongoClient
from tabulate import tabulate


def main():
    client = MongoClient('mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority')
    stats = client.get_database('covid19').get_collection('statistics')
    metadata = client.get_database('covid19').get_collection('metadata')

    print('Most recent 10 statistics for the UK:')
    results = stats.find({'country': 'United Kingdom', "state": None}).sort('date', pymongo.DESCENDING).limit(10)
    print_table(
        ["date", "confirmed", "deaths"],
        results)


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


if __name__ == '__main__':
    main()
