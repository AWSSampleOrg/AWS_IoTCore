#!/usr/bin/env bash

. config.sh

# https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iot/update-indexing-configuration.html
aws iot update-indexing-configuration \
    --thing-indexing-configuration \
    'thingIndexingMode=REGISTRY_AND_SHADOW,
    thingConnectivityIndexingMode=STATUS,
    deviceDefenderIndexingMode=VIOLATIONS,
    namedShadowIndexingMode=ON,
    filter={
        namedShadowNames=[green-bulb-shadow,yellow-bulb-shadow,red-bulb-shadow]
    },
    customFields=[
        {name=attributes.wattage,type=Number},
        {name=shadow.name.green-bulb-shadow.desired.battery, type=Number},
        {name=shadow.name.green-bulb-shadow.reported.battery, type=Number},
    ]' \
    --thing-group-indexing-configuration \
    'thingGroupIndexingMode=ON,
    customFields=[
        {name=attributes.wattage,type=Number}
    ]'

sleep 20

aws iot create-dynamic-thing-group \
    --thing-group-name LessThan50PercentInBattery \
    --query-string "attributes.wattage < 50"
