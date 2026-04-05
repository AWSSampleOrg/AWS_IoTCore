https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html

## Normal rule actions

### Devices -> Device Gateway -> Message Broker -> Rule Engine

## Basic Ingest

Your devices and rules can't subscribe to Basic Ingest reserved topics. For example, the AWS IoT Device Defender metric num-messages-received metrics is not emitted as it doesn't support subscribing to topics.

### Devices -> Device Gateway -> Rule Engine

```sh
$aws/rules/<IoT Rule Name>/<The topic name specified in the left IoT Rule>
```

For example, "BuildingManager" is a rule name and "Buildings/Building5/Floor2/Room201/Lights" is a MQTT topic

```sh
$aws/rules/BuildingManager/Buildings/Building5/Floor2/Room201/Lights
```
