# Managing Fleet Indexing

Combined CloudFormation template for both thing indexing and thing group indexing.

## Quick Start

```bash
./deploy.sh
sleep 30
```

## What It Creates

- **mything1, mything2** - Things with attributes
- **MyThingType** - Thing type
- **mygroup1, mygroup2** - Thing groups
- **mythinggroup1, mythinggroup2** - Additional thing groups

## Deploy

```bash
./deploy.sh [stack-name]
```

This will:

1. Deploy CloudFormation stack (creates IoT resources)
2. Run `fleet_indexing.py` to configure indexing

## Configure Fleet Indexing

Edit `fleet_indexing.py` to modify indexing configuration, then run:

```bash
# Enable
python fleet_indexing.py enable

# Disable
python fleet_indexing.py disable
```

## Test

```bash
# Thing indexing tests
cd thing-indexing
./test-queries.sh

# Thing group indexing tests
cd thing-group-indexing
./test-queries.sh

# Update shadows
cd thing-indexing
./update-shadows.sh
```

## Delete

```bash
python fleet_indexing.py disable
aws cloudformation delete-stack --stack-name fleet-indexing-test
```

## References

- [Manage Thing Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html)
- [Manage Thing Group Indexing](https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html)
