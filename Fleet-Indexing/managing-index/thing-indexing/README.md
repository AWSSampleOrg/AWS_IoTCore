# Thing Indexing Tests

Detailed test queries based on [AWS IoT documentation](https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html).

## Usage

Deploy from parent directory:

```bash
cd ..
./deploy.sh
sleep 30
cd thing-indexing
./test-queries.sh
```

## Update Shadows

```bash
./update-shadows.sh
```

## Tests

1. Describe Index Status
2. Get Indexing Configuration
3. Search by Thing Name
4. Search by Attribute (country:usa)
5. Search by Shadow (battery>70)
6. Search by Connectivity Status
7. Search by Thing Type

## References

- [Manage Thing Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html)
