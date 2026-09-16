# Basic Ingest

https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html

### Normal rule actions

```
Devices -> Device Gateway -> Message Broker -> Rule Engine
```

### Basic Ingest

```
Devices -> Device Gateway -> Rule Engine
```

```sh
$aws/rules/<IoT Rule Name>/<the topic the rule would normally be invoked by>
```

## FROM

https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html

```
If you define a rule that's invoked only with Basic Ingest, the FROM clause is optional in the sql field of the rule definition.
```

`FROM 'test/basic-ingest'` still fired on `$aws/rules/TopicRuleForBasicIngest/no/match/here`. `WHERE 1 = 2` did not run the actions, so only FROM is bypassed.

## topic()

https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html

```
The initial prefix of a Basic Ingest topic ($aws/rules/rule_name) isn't available to the topic(Decimal) function.
```

## Cannot subscribe

https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html

```
Your devices and rules can't subscribe to Basic Ingest reserved topics.
```

# How to test

Run client.py

```sh
python client.py
```

And Publish data on a different terminal

```sh
./publish.sh
```
