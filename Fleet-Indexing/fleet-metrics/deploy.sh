#!/usr/bin/env bash
# Based on https://docs.aws.amazon.com/iot/latest/developerguide/fleet-metrics-get-started.html

echo "=== Fleet Metrics Setup ==="
echo ""

echo "Step 1: Enable Fleet Indexing"
aws iot update-indexing-configuration \
  --thing-indexing-configuration "thingIndexingMode=REGISTRY_AND_SHADOW,customFields=[{name=attributes.temperature,type=Number},{name=attributes.rackId,type=String},{name=attributes.stateNormal,type=Boolean}],thingConnectivityIndexingMode=STATUS"

echo ""
echo "Step 2: Create 10 test things (TempSensor0-9)"

Temperatures=(70 71 72 73 74 75 47 97 98 99)
Racks=(Rack1 Rack1 Rack2 Rack2 Rack3 Rack4 Rack5 Rack6 Rack6 Rack6)
IsNormal=(true true true true true true false false false false)

for ((i=0; i < 10; i++))
do
  aws iot create-thing --thing-name "TempSensor$i" \
    --attribute-payload attributes="{temperature=${Temperatures[@]:$i:1},rackId=${Racks[@]:$i:1},stateNormal=${IsNormal[@]:$i:1}}"
  echo "Created TempSensor$i"
done

echo ""
echo "Step 3: Create fleet metric"
aws iot create-fleet-metric \
  --metric-name "high_temp_FM" \
  --query-string "thingName:TempSensor* AND attributes.temperature >80" \
  --period 60 \
  --aggregation-field "attributes.temperature" \
  --aggregation-type name=Statistics,values=count

echo ""
echo "Fleet metric created! View in CloudWatch after a few minutes."
