#!/usr/bin/env bash
exit_code=0
mongo "${1}" --quiet --eval "db.dropDatabase()"
exit_code=$((exit_code + $?))

for file in jhu/csse_covid_19_data/csse_covid_19_daily_reports/*.csv; do
  echo "==> ${file}"
  mongoimport --uri "${1}" --collection daily --type csv --headerline --file "${file}" --writeConcern='{w: 1, wtimeout: 60000, j: true}'
  exit_code=$((exit_code + $?))
done

for file in jhu/csse_covid_19_data/csse_covid_19_daily_reports_us/*.csv; do
  mongoimport --uri "${1}" --collection daily_us --type csv --headerline --file "${file}" --writeConcern='{w: 1, wtimeout: 60000, j: true}'
  exit_code=$((exit_code + $?))
done

for file in jhu/csse_covid_19_data/csse_covid_19_time_series/*.csv; do
  mongoimport --uri "${1}" --collection "$(basename "${file}" .csv)" --type csv --headerline --file "${file}" --writeConcern='{w: 1, wtimeout: 60000, j: true}'
  exit_code=$((exit_code + $?))
done

mongoimport --uri "${1}" --collection UID_ISO_FIPS_LookUp_Table --type csv --headerline --file jhu/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv --writeConcern='{w: 1, wtimeout: 60000, j: true}'
exit_code=$((exit_code + $?))

echo "$0 finished with code $exit_code."
exit $exit_code
