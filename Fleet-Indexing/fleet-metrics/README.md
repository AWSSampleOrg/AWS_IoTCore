# Fleet Metrics

Based on [AWS IoT Fleet Metrics Tutorial](https://docs.aws.amazon.com/iot/latest/developerguide/fleet-metrics-get-started.html).

## Quick Start

```bash
chmod +x deploy.sh cleanup.sh
./deploy.sh
# Wait a few minutes, then view in CloudWatch
./cleanup.sh  # When done
```

## What It Does (from AWS tutorial)

Creates a fleet metric to monitor sensors with temperatures > 80°F:

- Enables fleet indexing with custom fields (temperature, rackId, stateNormal)
- Creates 10 things (TempSensor0-9) with temperature attributes
- Creates fleet metric `high_temp_FM` that runs every 60 seconds
- Emits count to CloudWatch

## Documentation Example

```bash
# Create fleet metric (from tutorial)
aws iot create-fleet-metric \
  --metric-name "high_temp_FM" \
  --query-string "thingName:TempSensor* AND attributes.temperature >80" \
  --period 60 \
  --aggregation-field "attributes.temperature" \
  --aggregation-type name=Statistics,values=count

# Describe fleet metric
aws iot describe-fleet-metric --metric-name "high_temp_FM"

# Delete fleet metric
aws iot delete-fleet-metric --metric-name "high_temp_FM"
```

## View in CloudWatch

1. Open CloudWatch console
2. Go to Metrics → All metrics
3. Select **IoTFleetMetrics**
4. Choose **Aggregation type**
5. Select your fleet metric to view graph

## References

- [Fleet Metrics](https://docs.aws.amazon.com/iot/latest/developerguide/iot-fleet-metrics.html)
- [Getting Started Tutorial](https://docs.aws.amazon.com/iot/latest/developerguide/fleet-metrics-get-started.html)
