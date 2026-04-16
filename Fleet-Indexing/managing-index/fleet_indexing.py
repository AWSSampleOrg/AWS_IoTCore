import boto3
import sys

iot = boto3.client("iot")

# Configuration - Update these to match your stack
STACK_NAME = "fleet-indexing-test"
THING1_NAME = f"{STACK_NAME}-mything1"
THING2_NAME = f"{STACK_NAME}-mything2"
THING_TYPE_NAME = f"{STACK_NAME}-MyThingType"
GROUP1_NAME = f"{STACK_NAME}-mygroup1"
GROUP2_NAME = f"{STACK_NAME}-mygroup2"


def update_fleet_indexing():
    """Enable fleet indexing for both things and thing groups."""
    try:
        print(f"Assigning thing type {THING_TYPE_NAME} to {THING2_NAME}...")
        iot.update_thing(thingName=THING2_NAME, thingTypeName=THING_TYPE_NAME)

        config = {
            "thingIndexingMode": "REGISTRY_AND_SHADOW",
            "thingConnectivityIndexingMode": "STATUS",
            "namedShadowIndexingMode": "ON",
            "filter": {"namedShadowNames": ["thing1shadow"]},
            "customFields": [
                {"name": "attributes.model", "type": "String"},
                {"name": "attributes.country", "type": "String"},
                {"name": "shadow.reported.location", "type": "String"},
                {"name": "shadow.reported.stats.battery", "type": "Number"},
                {
                    "name": "shadow.name.thing1shadow.desired.DefaultDesired",
                    "type": "String",
                },
            ],
        }

        print("Enabling fleet indexing...")
        iot.update_indexing_configuration(
            thingIndexingConfiguration=config,
            thingGroupIndexingConfiguration={"thingGroupIndexingMode": "ON"},
        )

        print("Adding things to groups...")
        for group, thing in [
            (GROUP1_NAME, THING1_NAME),
            (GROUP1_NAME, THING2_NAME),
            (GROUP2_NAME, THING2_NAME),
        ]:
            iot.add_thing_to_thing_group(thingGroupName=group, thingName=thing)
            print(f"  Added {thing} to {group}")

        print("Fleet indexing enabled successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise


def delete_fleet_indexing():
    """Disable fleet indexing for both things and thing groups."""
    try:
        print("Disabling fleet indexing...")
        iot.update_indexing_configuration(
            thingIndexingConfiguration={"thingIndexingMode": "OFF"},
            thingGroupIndexingConfiguration={"thingGroupIndexingMode": "OFF"},
        )
        print("Fleet indexing disabled successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Enable:  python fleet_indexing.py enable")
        print("  Disable: python fleet_indexing.py disable")
    else:
        command = sys.argv[1]
        if command == "enable":
            update_fleet_indexing()
        elif command == "disable":
            delete_fleet_indexing()
        else:
            print(f"Unknown command: {command}")
