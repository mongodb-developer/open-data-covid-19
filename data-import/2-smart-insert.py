import csv
import sys
import time
from collections import OrderedDict
from datetime import datetime

import pymongo
from pymongo import MongoClient


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
    if string == 'Country_Region':
        return 'country'
    if string == 'Admin2':
        return 'city'
    if string == 'Province_State' or string == 'Province/State':
        return 'state'
    if string == 'Combined_Key':
        return 'combined_name'
    return str.lower(string)


def is_blank(s):
    return not bool(s and s.strip())


def geo_loc(doc):
    try:
        lat = float(doc.pop('lat'))
        long = float(doc.pop('long'))
        if lat != 0.0 and long != 0.0:
            doc['loc'] = {'type': 'Point', 'coordinates': [long, lat]}
    except KeyError:
        return


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


def data_hacking(recovered, fips, confirmed_us, deaths_us):
    # Fixing data for Canada
    for d in recovered:
        if d.get('country') == 'Canada' and is_blank(d.get('state')):
            d['state'] = 'Recovered'
    # Fixing Falkland Islands
    for d in fips:
        if d.get('state') == 'Falkland Islands (Malvinas)':
            d['state'] = 'Falkland Islands (Islas Malvinas)'


def print_warnings(deaths, recovered, deaths_us):
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


def combine_global_and_fips(confirmed_global, deaths_global, recovered_global, fips):
    combined = []
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
            print("No FIPS found for", doc['country'], '=>', doc)

        combined.append({'confirmed_global': doc, 'deaths_global': doc1, 'recovered_global': doc2, 'fips': doc3})
    return combined


def combine_us_and_fips(confirmed_us, deaths_us, fips):
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
            print("No UID found for", doc['combined_name'], '=>', doc)

        combined.append({'confirmed_us': doc, 'deaths_us': doc1, 'fips': doc2})
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
                    if cg['country'] != 'US':
                        doc['confirmed'] = v1

                    for k2, v2 in dg.items():
                        if k1 == k2 and cg['country'] != 'US':
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

    return mdb_docs


def get_mongodb_client():
    uri = sys.argv[1]
    if not uri:
        print('MongoDB URI is missing in cmd line arg 1.')
        exit(1)
    return MongoClient(uri)


def mongodb_insert(client, docs):
    coll = client.get_database('coronavirus').get_collection('statistics')
    coll.drop()
    return coll.insert_many(docs)


def create_indexes(client):
    coll = client.get_database('coronavirus').get_collection('statistics')
    coll.create_index([('country', pymongo.ASCENDING), ('state', pymongo.ASCENDING), ('city', pymongo.ASCENDING)])
    coll.create_index('country_iso3')
    coll.create_index('uid')
    coll.create_index('date')
    coll.create_index([("loc", pymongo.GEOSPHERE)])


def create_metadata(client):
    coll = client.get_database('coronavirus').get_collection('statistics')
    countries = list(coll.distinct('country'))
    states = list(coll.distinct('state'))
    cities = list(coll.distinct('city'))
    iso3s = list(coll.distinct('country_iso3'))
    uids = list(coll.distinct('uid'))
    dates = list(coll.aggregate([{'$sort': {'date': 1}}, {'$group': {'_id': None, 'first': {'$first': '$date'}, 'last': {'$last': '$date'}}}, {'$project': {'_id': 0}}]))[0]

    metadata_coll = client.get_database('coronavirus').get_collection('metadata')
    metadata_coll.delete_one({'_id': 'metadata'})
    metadata_coll.insert_one(
        {'_id': 'metadata', 'countries': countries, 'states': states, 'cities': cities, 'iso3s': iso3s, 'uids': uids, 'first_date': dates['first'], 'last_date': dates['last']})


def main():
    start = time.time()
    fips, confirmed_global, deaths_global, recovered_global, confirmed_us, deaths_us = clean_all_docs(get_all_csv_as_docs())
    data_hacking(recovered_global, fips, confirmed_us, deaths_us)
    combined_global = combine_global_and_fips(confirmed_global, deaths_global, recovered_global, fips)
    combined_us = combine_us_and_fips(confirmed_us, deaths_us, fips)
    print_warnings(deaths_global, recovered_global, deaths_us)
    combined = combined_global + combined_us
    docs = doc_generation(combined)
    print(len(docs), 'documents have been generated in', round(time.time() - start, 2), 's')
    start = time.time()
    client = get_mongodb_client()
    print(len(mongodb_insert(client, docs).inserted_ids), 'have been inserted in', round(time.time() - start, 2), 's')
    start = time.time()
    create_indexes(client)
    create_metadata(client)
    print('Creating indexes and metadata in', round(time.time() - start, 2), 's')


if __name__ == '__main__':
    main()
