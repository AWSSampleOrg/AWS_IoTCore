# AWS IoT Fleet Indexing

Fleet indexing allows you to index, search, and aggregate your devices' data from multiple sources.

## Documentation Structure

This repository mirrors the [AWS IoT Fleet Indexing documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-indexing.html):

```
Fleet-Indexing/
├── managing-index/              # Managing fleet indexing
│   ├── thing-indexing/          # Manage thing indexing
│   └── thing-group-indexing/    # Manage thing group indexing
├── query-examples/              # Query syntax examples
├── aggregation-queries/         # Aggregate data queries
└── fleet-metrics/               # Fleet metrics with CloudWatch
```

**Mapping to AWS Docs:**

- `managing-index/thing-indexing/` → [Manage thing indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html)
- `managing-index/thing-group-indexing/` → [Manage thing group indexing](https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html)
- `query-examples/` → [Query syntax](https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html)
- `aggregation-queries/` → [Querying for aggregate data](https://docs.aws.amazon.com/iot/latest/developerguide/index-aggregate.html)
- `fleet-metrics/` → [Fleet metrics](https://docs.aws.amazon.com/iot/latest/developerguide/iot-fleet-metrics.html)

## Quick Start

### Thing Indexing

```bash
cd managing-index/thing-indexing
chmod +x deploy.sh test-queries.sh
./deploy.sh
sleep 30
./test-queries.sh
```

See [managing-index/thing-indexing/README.md](managing-index/thing-indexing/README.md) for details.

## Features

- **Registry data**: Thing names, attributes, thing types
- **Shadow data**: Device state (classic and named shadows)
- **Connectivity status**: Device connection state
- **Device Defender violations**: Security profile violations
- **Aggregation queries**: Statistics, percentiles, cardinality
- **Fleet metrics**: CloudWatch integration

## References

- [Fleet Indexing Documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-indexing.html)
- [Managing Fleet Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-fleet-index.html)
- [Query Syntax](https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html)

## Manual Testing

### 1. Enable Fleet Indexing

```bash
aws iot update-indexing-configuration \
  --thing-indexing-configuration '{
    "thingIndexingMode": "REGISTRY_AND_SHADOW",
    "thingConnectivityIndexingMode": "STATUS"
  }'
```

### 2. Check Index Status

```bash
aws iot describe-index --index-name "AWS_Things"
```

### 3. Create Test Thing

```bash
aws iot create-thing \
  --thing-name "my-sensor" \
  --attribute-set temperature=25 location="zone-1"
```

### 4. Update Shadow

```bash
aws iot-data update-thing-shadow \
  --thing-name "my-sensor" \
  --payload '{"state":{"reported":{"battery":85,"status":"online"}}}' \
  /tmp/shadow.json
```

### 5. Search Index

```bash
# Find all things
aws iot search-index --index-name "AWS_Things" --query-string "*"

# Find by attribute
aws iot search-index --index-name "AWS_Things" --query-string "attributes.temperature>20"

# Find by shadow
aws iot search-index --index-name "AWS_Things" --query-string "shadow.reported.battery>80"
```

### 6. Aggregation Query

```bash
aws iot get-statistics \
  --index-name "AWS_Things" \
  --query-string "*" \
  --aggregation-field "attributes.temperature"
```

### 7. Disable Fleet Indexing

```bash
aws iot update-indexing-configuration \
  --thing-indexing-configuration '{"thingIndexingMode": "OFF"}'
```

## Query Syntax Examples

- `thingName:sensor*` - Wildcard search
- `attributes.temperature:[20 TO 30]` - Range query
- `shadow.reported.battery>80` - Comparison
- `attributes.location:zone-1 AND attributes.temperature>25` - Boolean logic
- `connectivity.connected:true` - Connectivity status

## References

- [Fleet Indexing Documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-indexing.html)
- [Managing Fleet Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-fleet-index.html)
- [Query Syntax](https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html)
