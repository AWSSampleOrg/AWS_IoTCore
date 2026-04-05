- https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-mqtt.html
- https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html#reserved-topics-shadow

# Named shadow

```
$aws/things/thingName/shadow/name/shadowName/get
$aws/things/thingName/shadow/name/shadowName/get/accepted
$aws/things/thingName/shadow/name/shadowName/get/rejected
$aws/things/thingName/shadow/name/shadowName/update
$aws/things/thingName/shadow/name/shadowName/update/delta
$aws/things/thingName/shadow/name/shadowName/update/accepted
$aws/things/thingName/shadow/name/shadowName/update/documents
$aws/things/thingName/shadow/name/shadowName/update/rejected
$aws/things/thingName/shadow/name/shadowName/delete
$aws/things/thingName/shadow/name/shadowName/delete/accepted
$aws/things/thingName/shadow/name/shadowName/delete/rejected
```

# Classic shadow

```
$aws/things/thingName/shadow/get
$aws/things/thingName/shadow/get/accepted
$aws/things/thingName/shadow/get/rejected
$aws/things/thingName/shadow/update
$aws/things/thingName/shadow/update/delta
$aws/things/thingName/shadow/update/accepted
$aws/things/thingName/shadow/update/documents
$aws/things/thingName/shadow/update/rejected
$aws/things/thingName/shadow/delete
$aws/things/thingName/shadow/delete/accepted
$aws/things/thingName/shadow/delete/rejected
```
