#!/usr/bin/env bash
source .env

mongo mongodb+srv://covid-19.hip2i.mongodb.net/covid19 --username ${MDB_USER} --password ${MDB_PWD} --quiet --eval "db.dropDatabase()"

for file in jhu/csse_covid_19_data/csse_covid_19_daily_reports/*.csv
do
#  docker run --rm -v $(pwd)/jhu:/jhu mongo:4.2.5 mongoimport --uri mongodb+srv://${MDB_USER}:${MDB_PWD}@covid-19.hip2i.mongodb.net/covid19 --ssl --collection daily --type csv --headerline --file /${file}
  mongoimport --uri mongodb+srv://${MDB_USER}:${MDB_PWD}@covid-19.hip2i.mongodb.net/covid19 --collection daily --type csv --headerline --file ${file} &
done
wait

for file in jhu/csse_covid_19_data/csse_covid_19_time_series/*.csv
do
#  docker run --rm -v $(pwd)/jhu:/jhu mongo:4.2.5 mongoimport --uri mongodb+srv://${MDB_USER}:${MDB_PWD}@covid-19.hip2i.mongodb.net/covid19 --ssl --collection $(basename ${file} .csv) --type csv --headerline --file /${file}
  mongoimport --uri mongodb+srv://${MDB_USER}:${MDB_PWD}@covid-19.hip2i.mongodb.net/covid19 --collection $(basename ${file} .csv) --type csv --headerline --file ${file} &
done
wait

mongoimport --uri mongodb+srv://${MDB_USER}:${MDB_PWD}@covid-19.hip2i.mongodb.net/covid19 --collection UID_ISO_FIPS_LookUp_Table --type csv --headerline --file jhu/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv

echo "Job done!"