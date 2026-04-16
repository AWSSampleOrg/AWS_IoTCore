# Query Examples

Examples of Fleet Indexing query syntax.

## Basic Queries

```bash
# Wildcard search
aws iot search-index --index-name AWS_Things --query-string "thingName:sensor*"

# Exact match
aws iot search-index --index-name AWS_Things --query-string "attributes.location:zone-1"

# Range query
aws iot search-index --index-name AWS_Things --query-string "attributes.temperature:[20 TO 30]"

# Comparison operators
aws iot search-index --index-name AWS_Things --query-string "shadow.reported.battery>80"

# Boolean logic
aws iot search-index --index-name AWS_Things --query-string "attributes.location:zone-1 AND attributes.temperature>25"

# Connectivity status
aws iot search-index --index-name AWS_Things --query-string "connectivity.connected:true"
```

## References

- [Query Syntax](https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html)
