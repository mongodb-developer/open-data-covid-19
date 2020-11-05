import csv
import sys
import time
from collections import OrderedDict
from datetime import datetime

import pymongo
from pymongo import MongoClient

DB = 'covid19'
TEMP = '_temp'
COLL_countries = 'countries_summary' + TEMP
COLL_global_and_us = 'global_and_us' + TEMP
COLL_global = 'global' + TEMP
COLL_us = 'us_only' + TEMP
COLL_metadata = 'metadata'


def parse(val):
    val = clean(val)
    try:
        return int(val)
    except ValueError:
        try:
            return round(float(val), 4)
        except ValueError:
            return val


def clean(string):
    return string.strip('_, ')


def clean_key(string):
    string = clean(string)
    if string == 'Country_Region' or string == 'Country/Region':
        return 'country'
    if string == 'iso2':
        return 'country_iso2'
    if string == 'iso3':
        return 'country_iso3'
    if string == 'code3':
        return 'country_code'
    if string == 'Admin2':
        return 'county'
    if string == 'Province_State' or string == 'Province/State':
        return 'state'
    if string == 'Combined_Key':
        return 'combined_name'
    return str.lower(string)


def is_blank(s):
    return not bool(s and s.strip())


def geo_loc(doc):
    lat = float(doc.pop('lat', 0.0))
    long = float(doc.pop('long', 0.0))
    if lat != 0.0 and long != 0.0:
        doc['loc'] = {'type': 'Point', 'coordinates': [long, lat]}


def clean_docs(docs):
    docs_array = []
    for doc in docs:
        new_doc = {}
        for k, v in doc.items():
            if not is_blank(clean_key(v)):
                new_doc[clean_key(k)] = parse(v)
        geo_loc(new_doc)
        docs_array.append(new_doc)
    return docs_array


def find_same_area_country_state(docs, country, state):
    for d in docs:
        if d.get('country') == country and d.get('state') == state:
            return d


def find_same_area_uid(docs, fips):
    for d in docs:
        if d.get('uid') == fips:
            return d


def get_all_csv_as_docs():
    with open("jhu/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        fips = []
        for row in csv_file:
            fips.append(OrderedDict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        confirmed_global_docs = []
        for row in csv_file:
            confirmed_global_docs.append(OrderedDict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        deaths_global_docs = []
        for row in csv_file:
            deaths_global_docs.append(OrderedDict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        recovered_global_docs = []
        for row in csv_file:
            recovered_global_docs.append(OrderedDict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        confirmed_us_docs = []
        for row in csv_file:
            confirmed_us_docs.append(OrderedDict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        deaths_us_docs = []
        for row in csv_file:
            deaths_us_docs.append(OrderedDict(row))
    return fips, confirmed_global_docs, deaths_global_docs, recovered_global_docs, confirmed_us_docs, deaths_us_docs


def clean_all_docs(csvs):
    return map(lambda x: clean_docs(x), csvs)


def data_hacking(confirmed, deaths, recovered, confirmed_us, deaths_us):
    # Ignoring lines without an UID as it's corrupted data
    confirmed_us = [d for d in confirmed_us if not d.get('uid', '') == '']
    deaths_us = [d for d in deaths_us if not d.get('uid', '') == '']
    return confirmed_us, deaths_us


def print_warnings_and_exit_on_error(deaths, recovered, deaths_us):
    if len(deaths) != 0:
        print('These deaths have not been handled correctly:')
        for i in deaths:
            print(i)
    if len(recovered) != 0:
        print('These recovered have not been handled correctly:')
        for i in recovered:
            print(i)
    if len(deaths_us) != 0:
        print('These deaths have not been handled correctly:')
        for i in deaths_us:
            print(i)
    if len(deaths) != 0 or len(recovered) != 0 or len(deaths_us) != 0:
        exit(1)


def combine_global_and_fips(confirmed_global, deaths_global, recovered_global, fips):
    error_output = []
    combined = []
    remove_from_recovered = []

    for doc in confirmed_global:
        country = doc.get('country')
        state = doc.get('state')

        doc1 = find_same_area_country_state(deaths_global, country, state)
        if doc1:
            deaths_global.remove(doc1)

        doc2 = find_same_area_country_state(recovered_global, country, state)
        if doc2:
            recovered_global.remove(doc2)

        doc3 = find_same_area_country_state(fips, country, state)
        if doc3:
            fips.remove(doc3)
        else:
            error_output.append("No FIPS found for " + doc['country'] + ' => ' + str(doc))

        combined.append({'confirmed_global': doc, 'deaths_global': doc1, 'recovered_global': doc2, 'fips': doc3})

    for doc in recovered_global:
        country = doc.get('country')
        state = doc.get('state')

        doc3 = find_same_area_country_state(fips, country, state)
        if doc3:
            fips.remove(doc3)
        else:
            error_output.append("No FIPS found for " + doc['country'] + ' => ' + str(doc))

        combined.append({'confirmed_global': None, 'deaths_global': None, 'recovered_global': doc, 'fips': doc3})
        remove_from_recovered.append(doc)

    for doc in remove_from_recovered:
        recovered_global.remove(doc)

    if len(error_output) != 0:
        for i in error_output:
            print(i)
        exit(2)
    return combined


def combine_us_and_fips(confirmed_us, deaths_us, fips):
    error_output = []
    combined = []
    for doc in confirmed_us:
        uid_value = doc.get('uid')

        doc1 = find_same_area_uid(deaths_us, uid_value)
        if doc1:
            deaths_us.remove(doc1)

        doc2 = find_same_area_uid(fips, uid_value)
        if doc2:
            fips.remove(doc2)
        else:
            error_output.append("No UID found for " + doc['combined_name'] + ' => ' + str(doc))

        combined.append({'confirmed_us': doc, 'deaths_us': doc1, 'fips': doc2})

    if len(error_output) != 0:
        for i in error_output:
            print(i)
        exit(3)
    return combined


def to_iso_date(date):
    return datetime.strptime(date, '%m/%d/%y')


def doc_generation(combined):
    mdb_docs = []
    for docs in combined:
        cg = docs.get('confirmed_global')
        dg = docs.get('deaths_global')
        rg = docs.get('recovered_global')
        usc = docs.get('confirmed_us')
        usd = docs.get('deaths_us')
        fips = docs.get('fips')

        if cg:
            for k1, v1 in cg.items():
                if '/' in k1:
                    doc = fips.copy()
                    doc['date'] = to_iso_date(k1)
                    doc['confirmed'] = v1

                    for k2, v2 in dg.items():
                        if k1 == k2:
                            doc['deaths'] = v2

                    if rg:
                        for k3, v3 in rg.items():
                            if k1 == k3:
                                doc['recovered'] = v3
                    mdb_docs.append(doc)

        if usc:
            for k1, v1 in usc.items():
                if '/' in k1:
                    doc = fips.copy()
                    doc['date'] = to_iso_date(k1)
                    doc['confirmed'] = v1

                    for k2, v2 in usd.items():
                        if k1 == k2:
                            doc['deaths'] = v2
                    mdb_docs.append(doc)

        if not cg and rg:
            for k1, v1 in rg.items():
                if '/' in k1:
                    doc = fips.copy()
                    doc['date'] = to_iso_date(k1)
                    doc['recovered'] = v1
                    mdb_docs.append(doc)
    return mdb_docs


def get_mongodb_client():
    uri = sys.argv[1]
    if not uri:
        print('MongoDB URI is missing in cmd line arg 1.')
        exit(1)
    return MongoClient(uri)


def mongodb_insert_many(client, collection, docs):
    start = time.time()
    coll = client.get_database(DB).get_collection(collection)
    coll.drop()
    result = coll.insert_many(docs)
    print(len(result.inserted_ids), 'have been inserted in', collection, 'in', round(time.time() - start, 2), 's')


def create_indexes_generic(client, collection):
    coll = client.get_database(DB).get_collection(collection)
    coll.create_index([('country_iso3', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)
    coll.create_index([('uid', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], unique=True)
    coll.create_index('date')
    coll.create_index([("loc", pymongo.GEOSPHERE)], sparse=True)


def create_indexes_countries_collection(client, collection):
    coll = client.get_database(DB).get_collection(collection)
    coll.create_index('date')
    coll.create_index([('country', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], unique=True)
    coll.create_index([('country', pymongo.ASCENDING), ('states', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)
    coll.create_index([('uids', pymongo.ASCENDING), ('date', pymongo.ASCENDING)])
    coll.create_index([('country_iso3s', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)


def create_index_country_state(client, collection):
    coll = client.get_database(DB).get_collection(collection)
    coll.create_index([('country', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)
    coll.create_index([('country', pymongo.ASCENDING), ('state', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)


def create_index_country_state_county(client, collection):
    coll = client.get_database(DB).get_collection(collection)
    coll.create_index([('country', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)
    coll.create_index([('country', pymongo.ASCENDING), ('state', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)
    coll.create_index([('country', pymongo.ASCENDING), ('state', pymongo.ASCENDING), ('county', pymongo.ASCENDING), ('date', pymongo.ASCENDING)], sparse=True)


def create_indexes(client):
    start = time.time()
    create_indexes_generic(client, COLL_global)
    create_indexes_generic(client, COLL_us)
    create_indexes_generic(client, COLL_global_and_us)
    create_index_country_state(client, COLL_global)
    create_index_country_state_county(client, COLL_us)
    create_index_country_state_county(client, COLL_global_and_us)
    create_indexes_countries_collection(client, COLL_countries)
    print('Created indexes in ', round(time.time() - start, 2), 's')


def fix_double_count_us(client, collection):
    start = time.time()
    coll = client.get_database(DB).get_collection(collection)
    coll.update_many({'country': 'US', 'state': {'$exists': 0}}, {'$unset': {'deaths': '', 'confirmed': ''}})
    print('Removed double count for the US in collection', collection, 'in', round(time.time() - start, 2), 's')


def rename_collections(client, collections):
    start = time.time()
    for collection in collections:
        coll = client.get_database(DB).get_collection(collection)
        coll.rename(collection.replace(TEMP, ''), dropTarget=True)
    print('Renamed collections in', round(time.time() - start, 2), 's')


def create_metadata(client):
    start = time.time()
    coll = client.get_database(DB).get_collection(COLL_global_and_us.replace(TEMP, ''))
    coll_us = client.get_database(DB).get_collection(COLL_us.replace(TEMP, ''))
    countries = list(filter(None, coll.distinct('country')))
    states = list(filter(None, coll.distinct('state')))
    states_us = list(filter(None, coll_us.distinct('state')))
    counties = list(filter(None, coll.distinct('county')))
    iso3s = list(filter(None, coll.distinct('country_iso3')))
    uids = list(filter(None, coll.distinct('uid')))
    dates = list(coll.aggregate([{'$sort': {'date': 1}}, {'$group': {'_id': None, 'first': {'$first': '$date'}, 'last': {'$last': '$date'}}}, {'$project': {'_id': 0}}]))[0]

    metadata_coll = client.get_database(DB).get_collection(COLL_metadata)
    metadata_coll.delete_one({'_id': 'metadata'})
    metadata_coll.insert_one(
        {'_id': 'metadata', 'countries': countries, 'states': states, 'states_us': states_us, 'counties': counties, 'iso3s': iso3s, 'uids': uids, 'first_date': dates['first'],
         'last_date': dates['last']})
    print('Created metadata in', round(time.time() - start, 2), 's')


def create_collection_stats_countries(client):
    start = time.time()
    coll = client.get_database(DB).get_collection(COLL_global)
    pipeline = [
        {
            '$group': {
                '_id': {
                    'country': '$country',
                    'date': '$date'
                },
                'uids': {
                    '$addToSet': '$uid'
                },
                'country_iso2s': {
                    '$addToSet': '$country_iso2'
                },
                'country_iso3s': {
                    '$addToSet': '$country_iso3'
                },
                'country_codes': {
                    '$addToSet': '$country_code'
                },
                'combined_names': {
                    '$addToSet': '$combined_name'
                },
                'population': {
                    '$sum': '$population'
                },
                'confirmed': {
                    '$sum': '$confirmed'
                },
                'deaths': {
                    '$sum': '$deaths'
                },
                'recovered': {
                    '$push': '$recovered'
                },
                'states': {
                    '$push': '$state'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'country': '$_id.country',
                'date': '$_id.date',
                'uids': 1,
                'country_iso2s': {
                    '$cond': [
                        {
                            '$eq': [
                                '$country_iso2s', None
                            ]
                        }, '$$REMOVE', '$country_iso2s'
                    ]
                },
                'country_iso3s': {
                    '$cond': [
                        {
                            '$eq': [
                                '$country_iso3s', None
                            ]
                        }, '$$REMOVE', '$country_iso3s'
                    ]
                },
                'country_codes': {
                    '$cond': [
                        {
                            '$eq': [
                                '$country_codes', None
                            ]
                        }, '$$REMOVE', '$country_codes'
                    ]
                },
                'combined_names': {
                    '$cond': [
                        {
                            '$eq': [
                                '$combined_names', None
                            ]
                        }, '$$REMOVE', '$combined_names'
                    ]
                },
                'population': {
                    '$cond': [
                        {
                            '$eq': [
                                '$population', None
                            ]
                        }, '$$REMOVE', '$population'
                    ]
                },
                'confirmed': 1,
                'deaths': 1,
                'recovered': {
                    '$cond': [
                        {
                            '$eq': [
                                '$recovered', []
                            ]
                        }, '$$REMOVE', {
                            '$sum': '$recovered'
                        }
                    ]
                },
                'states': {
                    '$cond': [
                        {
                            '$eq': [
                                '$states', []
                            ]
                        }, '$$REMOVE', '$states'
                    ]
                }
            }
        }, {
            '$out': COLL_countries
        }
    ]
    coll.aggregate(pipeline, allowDiskUse=True)
    print('Created collection', COLL_countries, 'in', round(time.time() - start, 2), 's')


def calculate_daily_counts(client, collection, unique_daily_field):
    start = time.time()
    coll = client.get_database(DB).get_collection(collection)
    pipeline = [
        {"$sort": {unique_daily_field: 1, "date": 1}},
        {"$group": {"_id": "$" + unique_daily_field, "docs": {"$push": {"dt": "$date", "c": "$confirmed", "d": "$deaths", "r": "$recovered"}}}},
        {
            "$set": {
                "docs": {
                    "$map": {
                        "input": {"$range": [0, {"$size": "$docs"}]},
                        "as": "idx",
                        "in": {
                            "$let": {
                                "vars": {"d0": {"$arrayElemAt": ["$docs", {"$max": [0, {"$subtract": ["$$idx", 1]}]}]}, "d1": {"$arrayElemAt": ["$docs", "$$idx"]}},
                                "in": {"dt": "$$d1.dt", "dc": {"$subtract": ["$$d1.c", "$$d0.c"]}, "dd": {"$subtract": ["$$d1.d", "$$d0.d"]},
                                       "dr": {"$subtract": ["$$d1.r", "$$d0.r"]}}
                            }
                        }
                    }
                }
            }
        },
        {"$unwind": "$docs"},
        {"$project": {"_id": "$$REMOVE", unique_daily_field: "$_id", "date": "$docs.dt", "confirmed_daily": {"$ifNull": ["$docs.dc", "$$REMOVE"]},
                      "deaths_daily": {"$ifNull": ["$docs.dd", "$$REMOVE"]}, "recovered_daily": {"$ifNull": ["$docs.dr", "$$REMOVE"]}}},
        {"$merge": {"into": collection, "on": [unique_daily_field, "date"], "whenNotMatched": "fail"}}
    ]
    coll.aggregate(pipeline, allowDiskUse=True)
    print('Calculated daily fields for', collection, 'in', round(time.time() - start, 2), 's')


def main():
    start = time.time()
    fips, confirmed_global, deaths_global, recovered_global, confirmed_us, deaths_us = clean_all_docs(get_all_csv_as_docs())
    confirmed_us, deaths_us = data_hacking(confirmed_global, deaths_global, recovered_global, confirmed_us, deaths_us)
    combined_global = combine_global_and_fips(confirmed_global, deaths_global, recovered_global, fips)
    combined_us = combine_us_and_fips(confirmed_us, deaths_us, fips)
    print_warnings_and_exit_on_error(deaths_global, recovered_global, deaths_us)
    docs_global = doc_generation(combined_global)
    docs_us = doc_generation(combined_us)
    print(len(docs_global) + len(docs_us), 'documents have been generated in', round(time.time() - start, 2), 's')

    client = get_mongodb_client()
    mongodb_insert_many(client, COLL_global, docs_global)
    mongodb_insert_many(client, COLL_us, docs_us)
    mongodb_insert_many(client, COLL_global_and_us, docs_global + docs_us)
    create_collection_stats_countries(client)

    create_indexes(client)
    fix_double_count_us(client, COLL_global_and_us)
    calculate_daily_counts(client, COLL_us, "uid")
    calculate_daily_counts(client, COLL_global, "uid")
    calculate_daily_counts(client, COLL_global_and_us, "uid")
    calculate_daily_counts(client, COLL_countries, "country")

    rename_collections(client, [COLL_global, COLL_us, COLL_global_and_us, COLL_countries])
    create_metadata(client)


if __name__ == '__main__':
    main()
