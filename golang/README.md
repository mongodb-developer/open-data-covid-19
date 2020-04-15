# Go Sample Code

This directory contains sample code to get you started querying the COVID-19 open data collections with Golang.
This code was developed Go 1.14 - there are no guarantees it will work with earlier versions of Go.
All of the code can be found in [example/main.go](example/main.go).
If you have Go 1.14 installed you can build the sample code binary by running `make` in this directory.
The Makefile will build an executable in the current directory, called `golang_example`.
If you run `golang_example` the results should look something like this:

```text
open-data-covid-19/golang $ ./golang_example

Most recent 10 statistics for the UK:
+-------------------------------+-----------+-----------+--------+
|             DATE              | CONFIRMED | RECOVERED | DEATHS |
+-------------------------------+-----------+-----------+--------+
| 2020-04-14 00:00:00 +0000 UTC |     93873 |         0 |  12107 |
| 2020-04-13 00:00:00 +0000 UTC |     88621 |         0 |  11329 |
| 2020-04-12 00:00:00 +0000 UTC |     84279 |       344 |  10612 |
| 2020-04-11 00:00:00 +0000 UTC |     78991 |       344 |   9875 |
| 2020-04-10 00:00:00 +0000 UTC |     73758 |       344 |   8958 |
| 2020-04-09 00:00:00 +0000 UTC |     65077 |       135 |   7978 |
| 2020-04-08 00:00:00 +0000 UTC |     60733 |       135 |   7097 |
| 2020-04-07 00:00:00 +0000 UTC |     55242 |       135 |   6159 |
| 2020-04-06 00:00:00 +0000 UTC |     51608 |       135 |   5373 |
| 2020-04-05 00:00:00 +0000 UTC |     47806 |       135 |   4934 |
+-------------------------------+-----------+-----------+--------+

Last date loaded: 2020-04-14 00:00:00 +0000 UTC

The last day's highest reported recoveries:
+--------------+-----------+
|   COUNTRY    | RECOVERED |
+--------------+-----------+
| Germany      |     68200 |
| Spain        |     67504 |
| Hubei, China |     64363 |
| Iran         |     48129 |
| US           |     47763 |
+--------------+-----------+

The last day's confirmed cases for all the countries within 500km of Paris:
+--------------------------------+-----------+
|            COUNTRY             | CONFIRMED |
+--------------------------------+-----------+
| Switzerland                    |     25936 |
| Luxembourg                     |      3307 |
| Belgium                        |     31119 |
| Netherlands                    |     27419 |
| France                         |    130253 |
| Channel Islands, United        |       440 |
| Kingdom                        |           |
+--------------------------------+-----------+
```
