#!/usr/bin/env bash
docker run --rm --user "$(id -u)":"$(id -g)" -v "$(pwd)":/home -w /home -e MAVEN_CONFIG=/tmp/.m2 maven:3-jdk-8 mvn --quiet -Duser.home=/tmp compile exec:java -Dexec.mainClass="com.mongodb.coronavirus.MongoDB"
