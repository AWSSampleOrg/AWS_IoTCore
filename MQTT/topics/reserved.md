https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html

Asset Model and Device Management

- Asset Model Topics:
  - $aws/sitewise/asset-models/assetModelId/assets/assetId/properties/propertyId

- AWS IoT Device Defender Topics:
  - $aws/things/thingName/defender/metrics/payload-format
  - $aws/things/thingName/defender/metrics/payload-format/accepted
  - $aws/things/thingName/defender/metrics/payload-format/rejected

- AWS IoT Core Device Location Topics:
  - $aws/device_location/customer_device_id/get_position_estimate
  - $aws/device_location/customer_device_id/get_position_estimate/accepted
  - $aws/device_location/customer_device_id/get_position_estimate/rejected

- Commands Topics:
  - $aws/commands/devices/DeviceID/executions/ExecutionId/request/PayloadFormat
  - $aws/commands/devices/DeviceID/executions/ExecutionId/request
  - $aws/commands/devices/DeviceID/executions/ExecutionId/response/PayloadFormat
  - $aws/commands/devices/DeviceID/executions/ExecutionId/response/accepted/PayloadFormat
  - $aws/commands/devices/DeviceID/executions/ExecutionId/response/accepted
  - $aws/commands/devices/DeviceID/executions/ExecutionId/response/rejected/PayloadFormat
  - $aws/commands/devices/DeviceID/executions/ExecutionId/response/rejected
    Event Topics
    Events are triggered by registry changes, job status updates, or connection status.

- Certificates: $aws/events/certificates/registered/caCertificateId

- Jobs and Job Executions:
  - $aws/events/job/jobID/canceled
  - $aws/events/job/jobID/cancellation_in_progress
  - $aws/events/job/jobID/completed
  - $aws/events/job/jobID/deleted
  - $aws/events/job/jobID/deletion_in_progress
  - $aws/events/jobExecution/jobID/canceled
  - $aws/events/jobExecution/jobID/deleted
  - $aws/events/jobExecution/jobID/failed
  - $aws/events/jobExecution/jobID/rejected
  - $aws/events/jobExecution/jobID/removed
  - $aws/events/jobExecution/jobID/succeeded
  - $aws/events/jobExecution/jobID/timed_out

- Presence and Subscriptions:
  - $aws/events/presence/connected/clientId
  - $aws/events/presence/disconnected/clientId
  - $aws/events/subscriptions/subscribed/clientId
  - $aws/events/subscriptions/unsubscribed/clientId

- Registry (Things, Groups, and Types):
  - $aws/events/thing/thingName/created (also updated, deleted)
  - $aws/events/thingGroup/thingGroupName/created (also updated, deleted)
  - $aws/events/thingType/thingTypeName/created (also updated, deleted)
  - $aws/events/thingTypeAssociation/thing/thingName/thingTypeName
  - $aws/events/thingGroupMembership/thingGroup/thingGroupName/thing/thingName/added (or removed)
  - $aws/events/thingGroupHierarchy/thingGroup/parentThingGroupName/childThingGroup/childThingGroupName/added (or removed)
    Provisioning and Fleet Operations

- Fleet Provisioning:
  - $aws/certificates/create/payload-format (and /accepted, /rejected)
  - $aws/certificates/create-from-csr/payload-format (and /accepted, /rejected)
  - $aws/provisioning-templates/templateName/provision/payload-format (and /accepted, /rejected)

- Job Topics (Device MQTT API):
  - $aws/things/thingName/jobs/get (and /accepted, /rejected)
  - $aws/things/thingName/jobs/start-next (and /accepted, /rejected)
  - $aws/things/thingName/jobs/jobID/get (and /accepted, /rejected)
  - $aws/things/thingName/jobs/jobID/update (and /accepted, /rejected)
  - $aws/things/thingName/jobs/notify and $aws/things/thingName/jobs/notify-next
    Shadow, Tunneling, and Delivery

- Shadow Topics: These use a prefix based on whether the shadow is unnamed ($aws/things/thingName/shadow) or named ($aws/things/thingName/shadow/name/shadowName).
  - ShadowTopicPrefix/delete (and /accepted, /rejected)
  - ShadowTopicPrefix/get (and /accepted, /rejected)
  - ShadowTopicPrefix/update (and /accepted, /rejected, /delta, /documents)

- Rules and Secure Tunneling:
  - $aws/rules/ruleName
  - $aws/things/thing-name/tunnels/notify

- MQTT-based File Delivery:
  - $aws/things/thingName/streams/StreamId/data/payload-format
  - $aws/things/thingName/streams/StreamId/get/payload-format
  - $aws/things/thingName/streams/StreamId/description/payload-format
  - $aws/things/thingName/streams/StreamId/describe/payload-format
  - $aws/things/thingName/streams/StreamId/rejected/payload-format
