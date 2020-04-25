# MongoDB Open Data COVID-19

This project retrieves and inserts into [MongoDB](http://mongodb.com/) the [Johns Hopkins University](https://www.jhu.edu/) COVID-19 dataset provided on [Github](https://github.com/CSSEGISandData/COVID-19).

Please read the [blog post associated to this repository](https://developer.mongodb.com/article/johns-hopkins-university-covid-19-data-atlas).

## Databases and Collections

### Database covid19

This database contains a few collections that have been carefully engineered to be as useful and as convenient as possible to work with.

In each of these collections:

- the keys have been renamed correctly to provide more consistency across the different collections,
- the fields have been casted into their correct types,
- the loc fields contains [GeoJSON](https://geojson.org/) points,
- the date are ISODates,
- etc.

5 collections are available:

- metadata
- statistics (the most complete one)
- confirmed_recovered_deaths (the data from the time series global files)
- us_only (the data from the time series US files)
- countries_summary (same as confirmed_recovered_deaths but countries are grouped in a single doc for each date.)

#### Collection metadata

This collection contains only one single document. It contains the list of all the values (obtained with mongodb distinct function) for the major fields along with the first and last dates.

```shell script
{
  _id : "metadata",
  countries : [ "Afghanistan", "Albania", "Algeria", "..." ],
  states : [ "Alabama", "Alaska", "Alberta", "..." ],
  cities : [ "Abbeville", "Acadia", "Accomack", "..." ],
  iso3s : [ null, "ABW", "AFG", "..." ],
  uids : [ 4, 8, 12, ... ],
  first_date : 2020-01-22T00:00:00.000+00:00,
  last_date : 2020-04-24T00:00:00.000+00:00
}
```

#### Collection confirmed_recovered_deaths

This collection contains the equivalent of what is in the 3 documents:

- `time_series_covid19_confirmed_global.csv`
- `time_series_covid19_deaths_global.csv`
- `time_series_covid19_recovered_global.csv`

Each document is also joined with its associated line from the `UID_ISO_FIPS_LookUp_Table.csv` file.

In this collection we have `nb_entries(time_series_covid19_confirmed_global.csv) * number_days` documents.

Here is an example document:

```javascript
{
	"_id" : ObjectId("5ea45f2a8049cddb8cfa3822"),
	"uid" : 4,
	"country_iso2" : "AF",
	"country_iso3" : "AFG",
	"country_code" : 4,
	"country" : "Afghanistan",
	"combined_name" : "Afghanistan",
	"population" : 38928341,
	"loc" : {
		"type" : "Point",
		"coordinates" : [
			67.71,
			33.9391
		]
	},
	"date" : ISODate("2020-01-22T00:00:00Z"),
	"confirmed" : 0,
	"deaths" : 0,
	"recovered" : 0
}
```

#### Collection us_only

This collection contains the equivalent of what is in the 2 documents:

- `time_series_covid19_confirmed_US.csv`
- `time_series_covid19_deaths_US.csv`

Each document is also joined with its associated line from the `UID_ISO_FIPS_LookUp_Table.csv` file.

In this collection we have `nb_entries(time_series_covid19_confirmed_US.csv) * number_days` documents.

Here is an example document:

```javascript
{
	"_id" : ObjectId("5ea45f2b8049cddb8cfa9912"),
	"uid" : 16,
	"country_iso2" : "AS",
	"country_iso3" : "ASM",
	"country_code" : 16,
	"fips" : 60,
	"state" : "American Samoa",
	"country" : "US",
	"combined_name" : "American Samoa, US",
	"population" : 55641,
	"loc" : {
		"type" : "Point",
		"coordinates" : [
			-170.132,
			-14.271
		]
	},
	"date" : ISODate("2020-01-22T00:00:00Z"),
	"confirmed" : 0,
	"deaths" : 0
}
```

Note: JHU does not provide recovered data for the US files. It's currently only available in the global files.

#### Collection countries_summary

This collection is calculated using the data from the `confirmed_recovered_deaths` collection. It's the same collection but the countries are grouped together into a single document for each date.

So in this collection, you will find `nb_countries * nb_days` documents.

Also, because all the states are grouped into a single doc for each countries, some fields are arrays in this collection.

You can see the detailed aggregation pipeline in the `2-smart-insert.py` file in the `data-import` folder.

Here is an example for France:

```javascript
{
	"_id" : ObjectId("5ea47b661adaef5faa91478b"),
	"confirmed" : 6,
	"deaths" : 0,
	"country" : "France",
	"date" : ISODate("2020-02-02T00:00:00Z"),
	"country_iso2s" : [
		"PF",
		"BL",
		"FR",
		"NC",
		"PM",
		"MQ",
		"YT",
		"GP",
		"RE",
		"MF",
		"GF"
	],
	"country_iso3s" : [
		"GLP",
		"REU",
		"FRA",
		"GUF",
		"SPM",
		"PYF",
		"MYT",
		"MAF",
		"MTQ",
		"NCL",
		"BLM"
	],
	"country_codes" : [
		312,
		638,
		652,
		474,
		254,
		663,
		175,
		258,
		250,
		540,
		666
	],
	"combined_names" : [
		"Reunion, France",
		"New Caledonia, France",
		"Saint Barthelemy, France",
		"France",
		"Guadeloupe, France",
		"Martinique, France",
		"French Polynesia, France",
		"Mayotte, France",
		"Saint Pierre and Miquelon, France",
		"French Guiana, France",
		"St Martin, France"
	],
	"population" : 298682,
	"loc" : {
		"type" : "Point",
		"coordinates" : [
			-53,
			4
		]
	},
	"recovered" : 0,
	"states" : [
		"French Guiana",
		"French Polynesia",
		"Guadeloupe",
		"Mayotte",
		"New Caledonia",
		"Reunion",
		"Saint Barthelemy",
		"St Martin",
		"Martinique",
		"Saint Pierre and Miquelon"
	]
}
```

#### Collection statistics

This collection is the most complete collection in this database. This collection basically contains all the documents from the collections:

- `confirmed_recovered_deaths`
- `us_only`

But with a little trick on top: the US cases are counted in both collections respectively:

- at a country level in the first one,
- and in a more detailed level (city, county, state) in the second one.

So to take advantages of both collections, I just removed the confirmed and deaths counts from the US documents which comes from the `confirmed_recovered_deaths` collection.

This allow me to keep track of the recovered cases in the US while also keeping track of the confirmed and deaths cases at a more detailed level. This is really the best we can do here because JHU don't reported recovered cases at a detailed level for the US.

> With this trick, the count for confirmed, deaths and recovered persons for a given date is correct.

This is the collection I'm using to build my charts in my charts blog posts:

- [blog post on Developer Hub](https://developer.mongodb.com/article/coronavirus-map-live-data-tracker-charts),
- [blog post on the MongoDB blog](https://www.mongodb.com/blog/post/tracking-coronavirus-news-with-mongodb-charts).

The documents in this collection are exactly the same than in the collections mentioned above.

- For a document that comes from the `confirmed_recovered_deaths` collection:

```javascript
{
	"_id" : ObjectId("5ea49768865a48ecca6d5ccb"),
	"uid" : 250,
	"country_iso2" : "FR",
	"country_iso3" : "FRA",
	"country_code" : 250,
	"country" : "France",
	"combined_name" : "France",
	"population" : 65273512,
	"loc" : {
		"type" : "Point",
		"coordinates" : [
			2.2137,
			46.2276
		]
	},
	"date" : ISODate("2020-04-24T00:00:00Z"),
	"confirmed" : 158636,
	"deaths" : 22245,
	"recovered" : 43493
}
```

- For a document that comes from the `us_only` collection:

```javascript
{
	"_id" : ObjectId("5ea4976b865a48ecca70df4d"),
	"uid" : 84042101,
	"country_iso2" : "US",
	"country_iso3" : "USA",
	"country_code" : 840,
	"fips" : 42101,
	"city" : "Philadelphia",
	"state" : "Pennsylvania",
	"country" : "US",
	"combined_name" : "Philadelphia, Pennsylvania, US",
	"population" : 1584064,
	"loc" : {
		"type" : "Point",
		"coordinates" : [
			-75.1379,
			40.0034
		]
	},
	"date" : ISODate("2020-04-24T00:00:00Z"),
	"confirmed" : 11877,
	"deaths" : 449
}
```

- For the special document that comes from the `confirmed_recovered_deaths` collection and represents the US entire country (the one with the trick):

```javascript
{
	"_id" : ObjectId("5ea49768865a48ecca6d84d1"),
	"uid" : 840,
	"country_iso2" : "US",
	"country_iso3" : "USA",
	"country_code" : 840,
	"country" : "US",
	"combined_name" : "US",
	"population" : 329466283,
	"loc" : {
		"type" : "Point",
		"coordinates" : [
			-100,
			40
		]
	},
	"date" : ISODate("2020-04-24T00:00:00Z"),
	"recovered" : 99079
}
```

Just pay attention: the documents which come from the US detailed source don't have a `recovered` field because JHU doesn't provide this data. Only the documents (one for each date) that represents the US at a country level contain the `recovered` field.

Also JHU doesn't provide the recovered count for all the countries and states in the global files.

In this collection, we have `(nb_entries(time_series_covid19_confirmed_global.csv) + nb_entries(time_series_covid19_confirmed_global.csv)) * number_days`.

### Dabatase covid19jhu

This database contains the raw CSV files imported with the [mongoimport](https://docs.mongodb.com/manual/reference/program/mongoimport/) tool.

This database is updated by the `1-mongoimport-everything.sh` in the `data-import` folder.

This script imports all the files matching these names with wildcards:

- jhu/csse_covid_19_data/csse_covid_19_daily_reports/*.csv
- jhu/csse_covid_19_data/csse_covid_19_daily_reports_us/*.csv
- jhu/csse_covid_19_data/csse_covid_19_time_series/*.csv
- jhu/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv

And it creates these collections:

- Errata
- UID_ISO_FIPS_LookUp_Table
- daily
- daily_us
- time_series_covid19_confirmed_US
- time_series_covid19_confirmed_global
- time_series_covid19_deaths_US
- time_series_covid19_deaths_global
- time_series_covid19_recovered_global

> Note: These collections are not clean and the schema designs are not great to work with because they come from raw and flat CSV files but at least they contain exactly what JHU is delivering.