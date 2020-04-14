#!/usr/bin/env bash
docker run --rm -v "$(pwd)":/home -w /home maven:3-jdk-8 mvn --quiet compile exec:java -Dexec.mainClass="com.mongodb.coronavirus.MongoDB"
