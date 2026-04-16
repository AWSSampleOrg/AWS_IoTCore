#!/usr/bin/env bash
# Based on https://docs.aws.amazon.com/iot/latest/developerguide/fleet-metrics-get-started.html

echo "=== Cleaning up Fleet Metrics ==="
echo ""

echo "Deleting fleet metric..."
aws iot delete-fleet-metric --metric-name "high_temp_FM"

echo ""
echo "Deleting things..."
for ((i=0; i < 10; i++))
do
  aws iot delete-thing --thing-name "TempSensor$i"
  echo "Deleted TempSensor$i"
done

echo ""
echo "Cleanup complete!"
