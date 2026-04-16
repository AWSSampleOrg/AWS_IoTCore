# Thing Group Indexing Tests

Detailed test queries based on [AWS IoT documentation](https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html).

## Usage

Deploy from parent directory:

```bash
cd ..
./deploy.sh
sleep 30
cd thing-group-indexing
./test-queries.sh
```

## Tests

1. Get Indexing Configuration
2. Describe Index Status
3. Search Thing Groups

## References

- [Manage Thing Group Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html)
