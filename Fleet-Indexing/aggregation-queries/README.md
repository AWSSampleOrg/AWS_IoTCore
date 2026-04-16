# Aggregation Queries

Query aggregate data and return statistics about your fleet.

## Examples

```bash
# Count things by location
aws iot get-statistics \
  --index-name AWS_Things \
  --query-string "*" \
  --aggregation-field "attributes.location"

# Average temperature
aws iot get-statistics \
  --index-name AWS_Things \
  --query-string "*" \
  --aggregation-field "attributes.temperature"

# Battery statistics with percentiles
aws iot get-percentiles \
  --index-name AWS_Things \
  --query-string "*" \
  --aggregation-field "shadow.reported.battery" \
  --percents 25 50 75 90 99

# Cardinality (unique values)
aws iot get-cardinality \
  --index-name AWS_Things \
  --query-string "*" \
  --aggregation-field "attributes.deviceType"
```

## References

- [Querying for Aggregate Data](https://docs.aws.amazon.com/iot/latest/developerguide/index-aggregate.html)
