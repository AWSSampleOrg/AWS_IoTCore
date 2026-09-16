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

## Aggregation Query and APIs

An aggregation query is a definition, not an API call. It has three parts.

```
query-string        # which things to match (same syntax as search-index)
aggregation-field   # which field to aggregate (managed field, or custom field registered in step 1)
aggregation-type    # how to aggregate: Statics | Cardinality | Percentile
```

The same definition can run two ways:

- **On demand** `GetStatics`, `GetCardinality` and `GetPercentiles` return the value at the moment you call them.
- **On a schedule** `CreateFleetMetric` scores the definition and emits the result to CloudWatch every `period` seconds.

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
