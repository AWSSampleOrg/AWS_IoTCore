https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html

Asset Model and Device Management

## Asset Model Topics:

```
$aws/sitewise/asset-models/assetModelId/assets/assetId/properties/propertyId
```

## AWS IoT Device Defender Topics:

```
$aws/things/thingName/defender/metrics/payload-format
$aws/things/thingName/defender/metrics/payload-format/accepted
$aws/things/thingName/defender/metrics/payload-format/rejected
```

## AWS IoT Core Device Location Topics:

```
$aws/device_location/customer_device_id/get_position_estimate
$aws/device_location/customer_device_id/get_position_estimate/accepted
$aws/device_location/customer_device_id/get_position_estimate/rejected
```

## Commands Topics:

```
$aws/commands/devices/DeviceID/executions/ExecutionId/request/PayloadFormat
$aws/commands/devices/DeviceID/executions/ExecutionId/request
$aws/commands/devices/DeviceID/executions/ExecutionId/response/PayloadFormat
$aws/commands/devices/DeviceID/executions/ExecutionId/response/accepted/PayloadFormat
$aws/commands/devices/DeviceID/executions/ExecutionId/response/accepted
$aws/commands/devices/DeviceID/executions/ExecutionId/response/rejected/PayloadFormat
$aws/commands/devices/DeviceID/executions/ExecutionId/response/rejected
```

Event Topics
Events are triggered by registry changes, job status updates, or connection status.

## Certificates: $aws/events/certificates/registered/caCertificateId

## Jobs and Job Executions:

```
$aws/events/job/jobID/canceled
$aws/events/job/jobID/cancellation_in_progress
$aws/events/job/jobID/completed
$aws/events/job/jobID/deleted
$aws/events/job/jobID/deletion_in_progress
$aws/events/jobExecution/jobID/canceled
$aws/events/jobExecution/jobID/deleted
$aws/events/jobExecution/jobID/failed
$aws/events/jobExecution/jobID/rejected
$aws/events/jobExecution/jobID/removed
$aws/events/jobExecution/jobID/succeeded
$aws/events/jobExecution/jobID/timed_out
```

## Presence and Subscriptions:

```
$aws/events/presence/connected/clientId
$aws/events/presence/disconnected/clientId
$aws/events/subscriptions/subscribed/clientId
$aws/events/subscriptions/unsubscribed/clientId
```

## Registry (Things, Groups, and Types):

```
$aws/events/thing/thingName/created
$aws/events/thing/thingName/updated
$aws/events/thing/thingName/deleted
$aws/events/thingGroup/thingGroupName/created
$aws/events/thingGroup/thingGroupName/updated
$aws/events/thingGroup/thingGroupName/deleted
$aws/events/thingType/thingTypeName/created
$aws/events/thingType/thingTypeName/updated
$aws/events/thingType/thingTypeName/deleted
$aws/events/thingTypeAssociation/thing/thingName/thingTypeName
$aws/events/thingGroupMembership/thingGroup/thingGroupName/thing/thingName/added
$aws/events/thingGroupMembership/thingGroup/thingGroupName/thing/thingName/removed
$aws/events/thingGroupHierarchy/thingGroup/parentThingGroupName/childThingGroup/childThingGroupName/added
$aws/events/thingGroupHierarchy/thingGroup/parentThingGroupName/childThingGroup/childThingGroupName/removed
```

## Fleet Provisioning:

Provisioning and Fleet Operations

```
$aws/certificates/create/payload-format
$aws/certificates/create/payload-format/accepted
$aws/certificates/create/payload-format/rejected
$aws/certificates/create-from-csr/payload-format
$aws/certificates/create-from-csr/payload-format/accepted
$aws/certificates/create-from-csr/payload-format/rejected
$aws/provisioning-templates/templateName/provision/payload-format
$aws/provisioning-templates/templateName/provision/payload-format/accepted
$aws/provisioning-templates/templateName/provision/payload-format/rejected
```

## Job Topics (Device MQTT API):

```
$aws/things/thingName/jobs/get
$aws/things/thingName/jobs/get/accepted
$aws/things/thingName/jobs/get/rejected
$aws/things/thingName/jobs/start-next
$aws/things/thingName/jobs/start-next/accepted
$aws/things/thingName/jobs/start-next/rejected
$aws/things/thingName/jobs/jobID/get
$aws/things/thingName/jobs/jobID/get/accepted
$aws/things/thingName/jobs/jobID/get/rejected
$aws/things/thingName/jobs/jobID/update
$aws/things/thingName/jobs/jobID/update/accepted
$aws/things/thingName/jobs/jobID/update/rejected
$aws/things/thingName/jobs/notify
$aws/things/thingName/jobs/notify-next
```

Shadow, Tunneling, and Delivery

## Shadow Topics: These use a prefix based on whether the shadow is unnamed ($aws/things/thingName/shadow) or named ($aws/things/thingName/shadow/name/shadowName).

```
ShadowTopicPrefix/delete
ShadowTopicPrefix/delete/accepted
ShadowTopicPrefix/delete/rejected
ShadowTopicPrefix/get
ShadowTopicPrefix/get/accepted
ShadowTopicPrefix/get/rejected
ShadowTopicPrefix/update
ShadowTopicPrefix/update/accepted
ShadowTopicPrefix/update/rejected
ShadowTopicPrefix/update/delta
ShadowTopicPrefix/update/documents
```

## Rules and Secure Tunneling:

```
$aws/rules/ruleName
$aws/things/thing-name/tunnels/notify
```

## MQTT-based File Delivery:

```
$aws/things/thingName/streams/StreamId/data/payload-format
$aws/things/thingName/streams/StreamId/get/payload-format
$aws/things/thingName/streams/StreamId/description/payload-format
$aws/things/thingName/streams/StreamId/describe/payload-format
$aws/things/thingName/streams/StreamId/rejected/payload-format
```
