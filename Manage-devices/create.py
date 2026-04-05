import boto3
import json
import random

iot_core = boto3.client("iot")
iot_data = boto3.client("iot-data")


class IoTCore:
    def __init__(self) -> None:
        self.THING_TYPE_NAME = "LightBulb"
        self.THING_PARENT_GROUP_NAME = "LightBulbs"

    # certificates
    def create(self):
        iot_core.create_thing_group(
            thingGroupName=self.THING_PARENT_GROUP_NAME,
            thingGroupProperties={
                "attributePayload": {
                    "attributes": {"Manufacturer": "AnyCompany", "wattage": "60"}
                },
                "thingGroupDescription": "Generic bulb group",
            },
        )

        colors = "green" "yellow" "red"

        for color in colors:
            thing_group_name = f"{color}-bulb"
            iot_core.create_thing_group(
                thingGroupName=thing_group_name,
                parentGroupName=self.THING_PARENT_GROUP_NAME,
            )

            for i in range(1, 11):
                thing_name = f"{thing_group_name}-{i}"
                iot_core.create_thing(
                    thingName=thing_name,
                    thingTypeName=self.THING_TYPE_NAME,
                    attributePayload=json.dumps(
                        {"attributes": {"wattage": i, "model": i}}
                    ),
                )

                battery_health = random.randint(1, 100)
                iot_data.update_thing_shadow(
                    thingName=thing_name,
                    shadowName=f"{thing_group_name}-shadow",
                    payload=json.dumps(
                        {
                            "state": {
                                "desired": {"battery": battery_health},
                                "reported": {"battery": battery_health},
                            }
                        }
                    ),
                )

                iot_core.add_thing_to_thing_group(
                    thingName=thing_name, thingGroupName=thing_group_name
                )

        iot_core.update_indexing_configuration(
            thingIndexingConfiguration={
                "thingIndexingMode": "REGISTRY_AND_SHADOW",
                "thingConnectivityIndexingMode": "STATUS",
                "deviceDefenderIndexingMode": "VIOLATIONS",
                "namedShadowIndexingMode": "ON",
                "filter": {
                    "namedShadowNames": [
                        "green-bulb-shadow",
                        "yellow-bulb-shadow",
                        "red-bulb-shadow",
                    ]
                },
                "customFields": [
                    {"name": "attributes.wattage", "type": "Number"},
                    {
                        "name": "shadow.name.green-bulb-shadow.desired.battery",
                        "type": "Number",
                    },
                    {
                        "name": "shadow.name.green-bulb-shadow.reported.battery",
                        "type": "Number",
                    },
                ],
            },
            thingGroupIndexingConfiguration={
                "thingGroupIndexingMode": "ON",
                "customFields": [{"name": "attributes.wattage", "type": "Number"}],
            },
        )
        iot_core.create_dynamic_thing_group(
            thingGroupName="LessThan50PercentInBattery",
            queryString="attributes.wattage < 50",
        )


def main():
    iot_core_client = IoTCore()
    iot_core_client.create()


if __name__ == "__main__":
    main()
