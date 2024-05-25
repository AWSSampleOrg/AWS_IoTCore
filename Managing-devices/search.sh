#!/usr/bin/env bash

. config.sh

# https://docs.aws.amazon.com/iot/latest/developerguide/thing-registry.html
aws iot list-things --attribute-name "wattage" --attribute-value "7"
aws iot describe-thing --thing-name "red-bulb-7"

# https://docs.aws.amazon.com/iot/latest/developerguide/thing-types.html
aws iot describe-thing-type --thing-type-name $THING_TYPE_NAME

# https://docs.aws.amazon.com/iot/latest/developerguide/thing-groups.html#describe-thing-group
aws iot describe-thing-group --thing-group-name red-bulb

aws iot search-index --index-name "AWS_Things" --query-string "attributes.wattage = 7"

aws iot-data get-thing-shadow --thing-name red-bulb-6 --shadow-name red-bulb-shadow /dev/stdout | jq .
aws iot search-index --index-name "AWS_Things" --query-string "shadow.name.red-bulb-shadow.reported.battery:{70 TO 100}"
aws iot search-index \
    --index-name "AWS_Things" \
    --query-string "thingName:red-bulb*"
