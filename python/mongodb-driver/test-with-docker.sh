#!/usr/bin/env bash
docker run --rm --name pymongo-covid19-example -v $(pwd):/home -w /home python:3.8.2 /bin/bash -c "pip install -r requirements.txt; python example_queries.py"
