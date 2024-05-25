#!/usr/bin/env bash

. config.sh

colors=('green' 'yellow' 'red')
for color in "${colors[@]}"; do
    thing_group_name="${color}-bulb"
    aws iot delete-thing-group --thing-group-name $thing_group_name
    for i in $(seq 1 10); do
        thing_name="${thing_group_name}-$i"
        aws iot delete-thing \
            --thing-name ${thing_name}
    done
done

aws iot delete-thing-group --thing-group-name $THING_PARENT_GROUP_NAME
aws iot delete-dynamic-thing-group --thing-group-name LessThan50Wattage

aws iot update-indexing-configuration \
    --thing-indexing-configuration \
    'thingIndexingMode=OFF,
    thingConnectivityIndexingMode=OFF,
    namedShadowIndexingMode=OFF' \
    --thing-group-indexing-configuration \
    thingGroupIndexingMode=OFF

# # An error occurred (InvalidRequestException) when calling the DeleteThingType operation: Cannot delete thing type : LightBulb. Please wait for 5 minutes after deprecation and then retry
(aws iot deprecate-thing-type \
    --thing-type-name $THING_TYPE_NAME &&
    sleep 300 && aws iot delete-thing-type --thing-type-name $THING_TYPE_NAME) &
