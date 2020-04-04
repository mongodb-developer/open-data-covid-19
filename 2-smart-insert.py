import csv


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
        doc['loc'] = {'type': 'Point', 'coordinates': [long, lat]}
    except KeyError:
        return


def get_fips():
    with open("jhu/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        fips = []
        for row in csv_file:
            fips.append(dict(row))
        return fips


def clean_docs(docs):
    docs_array = []
    for doc in docs:
        # print("Before: " + str(doc))
        new_doc = {}
        for k, v in doc.items():
            if not is_blank(clean_key(v)):
                new_doc[clean_key(k)] = parse(v)
        geo_loc(new_doc)
        docs_array.append(new_doc)
        # print("After: " + str(new_doc))
    return docs_array


def find_same_area(docs, country, state):
    for d in docs:
        if d.get('country') == country and d.get('state') == state:
            return d


def get_ts_global():
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        confirmed_docs = []
        for row in csv_file:
            confirmed_docs.append(dict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        deaths_docs = []
        for row in csv_file:
            deaths_docs.append(dict(row))
    with open("jhu/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv", encoding="utf-8-sig") as file:
        csv_file = csv.DictReader(file)
        recovered_docs = []
        for row in csv_file:
            recovered_docs.append(dict(row))
    return confirmed_docs, deaths_docs, recovered_docs


def remove_us_data(confirmed, deaths, recovered):
    # Removing the US as we will add the detailed data for the US
    confirmed_us = {}
    deaths_us = {}
    recovered_us = {}
    for i in confirmed:
        if i.get('country') == 'US':
            confirmed_us = i
    for i in deaths:
        if i.get('country') == 'US':
            deaths_us = i
    for i in recovered:
        if i.get('country') == 'US':
            recovered_us = i
    confirmed.remove(confirmed_us)
    deaths.remove(deaths_us)
    recovered.remove(recovered_us)


def data_hacking(recovered, fips):
    # Fixing data for Canada
    for d in recovered:
        if d.get('country') == 'Canada' and is_blank(d.get('state')):
            d['state'] = 'Recovered'
    # Adding missing Malawi
    fips.append({'uid': 454, 'country_iso2': 'MW', 'country_iso3': 'MWI', 'country_code': 454, 'country': 'Malawi', 'combined_name': 'Malawi',
                 'loc': {'type': 'Point', 'coordinates': [34.3015, -13.2543]}})


def print_warnings(deaths, recovered):
    if len(deaths) != 0:
        print('These deaths have not been handled correctly:')
        for i in deaths:
            print(i)
    if len(recovered) != 0:
        print('These recovered have not been handled correctly:')
        for i in recovered:
            print(i)


confirmed, deaths, recovered = get_ts_global()
clean_confirmed = clean_docs(confirmed)
clean_deaths = clean_docs(deaths)
clean_recovered = clean_docs(recovered)
fips = clean_docs(get_fips())

data_hacking(clean_recovered, fips)
remove_us_data(clean_confirmed, clean_deaths, clean_recovered)

print(len(clean_confirmed), len(clean_deaths), len(clean_recovered), len(fips))

combined = []

for doc in clean_confirmed:
    same_area = []
    country = doc.get('country')
    state = doc.get('state')
    same_area.append(doc)

    doc1 = find_same_area(clean_deaths, country, state)
    if doc1:
        clean_deaths.remove(doc1)
        same_area.append(doc1)
    doc2 = find_same_area(clean_recovered, country, state)

    if doc2:
        clean_recovered.remove(doc2)
        same_area.append(doc2)
    doc = find_same_area(clean_deaths, country, state)

    doc3 = find_same_area(fips, country, state)
    if doc3:
        fips.remove(doc3)
        same_area.append(doc3)
    else:
        print("No FIPS found for", same_area[:1][0]['country'], '=>', same_area[:1])

    combined.append(same_area)

print(len(clean_confirmed), len(clean_deaths), len(clean_recovered), len(fips))
print(len(combined))

print_warnings(clean_deaths, clean_recovered)

# for i in combined:
#     print(len(i))

# for docs in clean_confirmed[:10]:
#     print(docs)
# print()
#
# for docs in clean_deaths[:10]:
#     print(docs)
# print()
#
# for docs in clean_recovered[:10]:
#     print(docs)
