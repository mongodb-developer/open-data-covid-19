#!/usr/bin/env bash
mongo "${1}" --quiet --eval "db.dropDatabase()"

for file in jhu/csse_covid_19_data/csse_covid_19_daily_reports/*.csv
do
  mongoimport --uri "${1}" --collection daily --type csv --headerline --file "${file}" &
done
wait

for file in jhu/csse_covid_19_data/csse_covid_19_daily_reports_us/*.csv
do
  mongoimport --uri "${1}" --collection daily_us --type csv --headerline --file "${file}" &
done
wait

for file in jhu/csse_covid_19_data/csse_covid_19_time_series/*.csv
do
  mongoimport --uri "${1}" --collection "$(basename "${file}" .csv)" --type csv --headerline --file "${file}" &
done
wait

mongoimport --uri "${1}" --collection UID_ISO_FIPS_LookUp_Table --type csv --headerline --file jhu/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv

echo "Job done!"