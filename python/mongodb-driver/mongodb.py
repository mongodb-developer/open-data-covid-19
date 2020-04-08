from datetime import datetime, timedelta

from pymongo import MongoClient


def main():
    client = MongoClient('mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority')
    coll = client.get_database('coronavirus').get_collection('statistics')
    two_days_ago = datetime.now() - timedelta(days=2)
    docs = list(coll.find({'country': 'France', 'date': {'$gt': two_days_ago}}))
    for d in docs:
        print(d)


if __name__ == '__main__':
    main()
