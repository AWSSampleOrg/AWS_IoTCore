# Fleet Indexing Repository Structure

This repository mirrors the AWS IoT Fleet Indexing documentation structure.

## Directory Mapping

```
Fleet-Indexing/
├── managing-index/
│   ├── thing-indexing/          → https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html
│   │   ├── template.yml         (CloudFormation: mything1, mything2, MyThingType, mygroup1, mygroup2)
│   │   ├── deploy.sh
│   │   ├── update-shadows.sh    (Updates shadows to match doc examples)
│   │   └── test-queries.sh      (All queries from documentation)
│   │
│   └── thing-group-indexing/    → https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html
│       ├── template.yml         (CloudFormation: mythinggroup1, mythinggroup2)
│       ├── deploy.sh
│       └── test-queries.sh      (AWS_ThingGroups index queries)
│
├── query-examples/              → https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html
│   └── test-queries.sh          (Query syntax examples: prefix, range, boolean, etc.)
│
├── aggregation-queries/         → https://docs.aws.amazon.com/iot/latest/developerguide/index-aggregate.html
│   └── test-queries.sh          (GetStatistics, GetCardinality, GetPercentiles, GetBucketsAggregation)
│
└── fleet-metrics/               → https://docs.aws.amazon.com/iot/latest/developerguide/fleet-metrics-get-started.html
    ├── deploy.sh                (Creates 10 TempSensor things + high_temp_FM metric)
    └── cleanup.sh               (Deletes fleet metric and things)
```

## Quick Start by Section

### Thing Indexing

```bash
cd managing-index/thing-indexing
./deploy.sh
sleep 30
./update-shadows.sh
./test-queries.sh
```

### Thing Group Indexing

```bash
cd managing-index/thing-group-indexing
./deploy.sh
sleep 30
./test-queries.sh
```

### Query Examples

```bash
cd query-examples
./test-queries.sh
```

### Aggregation Queries

```bash
cd aggregation-queries
./test-queries.sh
```

### Fleet Metrics

```bash
cd fleet-metrics
./deploy.sh
# View in CloudWatch after a few minutes
./cleanup.sh
```

## Documentation References

All examples are based on official AWS IoT documentation:

- [Fleet Indexing Overview](https://docs.aws.amazon.com/iot/latest/developerguide/iot-indexing.html)
- [Managing Fleet Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-fleet-index.html)
- [Manage Thing Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html)
- [Manage Thing Group Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html)
- [Query Syntax](https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html)
- [Querying for Aggregate Data](https://docs.aws.amazon.com/iot/latest/developerguide/index-aggregate.html)
- [Fleet Metrics](https://docs.aws.amazon.com/iot/latest/developerguide/iot-fleet-metrics.html)
- [Fleet Metrics Tutorial](https://docs.aws.amazon.com/iot/latest/developerguide/fleet-metrics-get-started.html)
