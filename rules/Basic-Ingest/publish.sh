#!/usr/bin/env bash

for topic in \
    '$aws/rules/TopicRuleForBasicIngest/test/basic-ingest' \
    '$aws/rules/TopicRuleForBasicIngest/no/match/here' \
    '$aws/rules/NoMatchRule/no/match/here' \
    'test/basic-ingest' ; do
    aws iot-data publish \
        --topic $topic \
        --qos 1 \
        --cli-binary-format raw-in-base64-out \
        --payload "{\"sent\":\"${topic}\"}"
done
