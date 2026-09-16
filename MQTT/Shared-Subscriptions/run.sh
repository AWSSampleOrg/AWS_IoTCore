#!/usr/bin/env bash

set -x

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

SUBSCRIBERS=(Subscriber1 Subscriber2 Subscriber3)

pids=()
for client_id in "${SUBSCRIBERS[@]}" ; do
    python -u client.py ${client_id} > ${client_id}.log 2>&1 &
    pids+=($!)
done

sleep 10

for index in $(seq 0 29) ; do
    aws iot-data publish \
        --topic 'shared-subscriptions/work' \
        --qos 1 \
        --cli-binary-format raw-in-base64-out \
        --payload "{\"index\":${index}}"
    sleep 0.2
done

sleep 5
kill -9 "${pids[@]}" 2>/dev/null
wait 2>/dev/null

set +x

for index in $(seq 0 29) ; do
    echo "${index} $(grep -n "\"index\": ${index}\$" *.log | tr '\n' ' ')"
done

for client_id in "${SUBSCRIBERS[@]}" ; do
    echo "${client_id} $(grep -c '"index"' ${client_id}.log)"
done
