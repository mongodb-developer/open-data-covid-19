import pymongo
from pymongo import MongoClient


def main():
    client = MongoClient('mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority')
    stats = client.get_database('covid19').get_collection('statistics')
    metadata = client.get_database('covid19').get_collection('metadata')

    print('Statistics for France, sorted by date descending, limit 20.')
    print_list(stats.find({'country': 'France', 'state': None}).sort('date', pymongo.DESCENDING).limit(15))

    print('\nMetadata')
    print_doc(metadata.find_one())

    print('\nIndex of the statistics collection.')
    print_list(stats.list_indexes())


def print_doc(doc):
    for k, v in doc.items():
        print(k, '=', v)


def print_list(docs):
    for d in docs:
        print(d)


if __name__ == '__main__':
    main()
