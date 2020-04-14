# Python & pymongo Code Sample

This code requires Python 3.6+ to work.

To run this code, create a virtual environment and install the project requirements into it:

```bash
# On Linux & OSX:
# (On Debian & Ubuntu linux, you may need to `apt install python-venv` first.)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# On Windows:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Once you've installed the dependencies, you can run the code sample as follows:

```sh
python3 example_queries.py
```

The output should look like this:

```txt
Most recent 10 statistics for the UK:
Date                   Confirmed    Deaths
-------------------  -----------  --------
2020-04-09 00:00:00        65077      7978
2020-04-08 00:00:00        60733      7097
2020-04-07 00:00:00        55242      6159
2020-04-06 00:00:00        51608      5373
2020-04-05 00:00:00        47806      4934
2020-04-04 00:00:00        41903      4313
2020-04-03 00:00:00        38168      3605
2020-04-02 00:00:00        33718      2921
2020-04-01 00:00:00        29474      2352
2020-03-31 00:00:00        25150      1789

The last day's highest reported recoveries:
Combined Name      Recovered
---------------  -----------
Hubei, China           64187
Germany                52407
Spain                  52165
Iran                   32309
Italy                  28470

The last day's confirmed cases for all the countries within 500km of Paris:
Combined Name                      Confirmed
-------------------------------  -----------
Switzerland                            24051
Luxembourg                              3115
Belgium                                24983
Netherlands                            21762
France                                117749
Channel Islands, United Kingdom          361
```
