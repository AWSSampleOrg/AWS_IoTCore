#!/usr/bin/env bash

. config.sh

aws iot describe-thing-type --thing-type-name $THING_TYPE_NAME
if [ $? -eq 0 ]; then
    aws iot deprecate-thing-type \
        --thing-type-name $THING_TYPE_NAME \
        --undo-deprecate
else
    aws iot create-thing-type \
        --thing-type-name $THING_TYPE_NAME \
        --thing-type-properties \
        'thingTypeDescription=light bulb type,
    searchableAttributes=wattage,model'
fi

# static group
# https://docs.aws.amazon.com/iot/latest/developerguide/thing-groups.html#create-thing-group
aws iot create-thing-group \
    --thing-group-name $THING_PARENT_GROUP_NAME \
    --thing-group-properties \
    'thingGroupDescription="Generic bulb group",
    attributePayload={
        attributes={
            Manufacturer=AnyCompany,wattage=60
        }
    }'

colors=('green' 'yellow' 'red')
for color in "${colors[@]}"; do
    thing_group_name="${color}-bulb"
    aws iot create-thing-group \
        --thing-group-name $thing_group_name \
        --parent-group-name $THING_PARENT_GROUP_NAME

    for i in $(seq 1 10); do
        thing_name="${thing_group_name}-$i"
        aws iot create-thing \
            --thing-name $thing_name \
            --thing-type-name $THING_TYPE_NAME \
            --attribute-payload "{\"attributes\": {\"wattage\":\"$i\", \"model\":\"$i\"}}"

        battery_health=$(($RANDOM % 100))
        aws iot-data update-thing-shadow \
            --thing-name $thing_name \
            --shadow-name "${thing_group_name}-shadow" \
            --cli-binary-format raw-in-base64-out \
            --payload '{ "state": { "desired": { "battery": '$battery_health' }, "reported": { "battery": '$battery_health' } } }' \
            /dev/null 2>&1

        aws iot add-thing-to-thing-group \
            --thing-name $thing_name \
            --thing-group-name $thing_group_name
    done
done

# dynamic group
# https://docs.aws.amazon.com/iot/latest/developerguide/dynamic-thing-groups.html
. dynamic_group.sh
