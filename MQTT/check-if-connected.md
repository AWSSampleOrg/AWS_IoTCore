# 1. [GetConnection](https://docs.aws.amazon.com/iot/latest/apireference/API_iotdata_GetConnection.html)

- Data persists 30 minutes after disconnect regardless of clean or persistent session.

```sh
aws iot-data get-connection --client-id <clientId>
```

`includeSocketInformation` adds `sourceIp`, `sourcePort`, `targetIp`, `targetPort` and `vpcEndpointId`. Only available here, not in `GetThingConnectivityData`, so this is the one to use when the network path or a VPC endpoint is in question. If the caller is not authorized to see socket data, the **whole call fails with 403** rather than returning a response without those fields.

```sh
aws iot-data get-connection --client-id <clientId> --include-socket-information
```

# 2. [GetThingConnectivityData](https://docs.aws.amazon.com/iot/latest/apireference/API_GetThingConnectivityData.html)

- You need to index `AWS_Things` using [UpdateIndexingConfiguration](https://docs.aws.amazon.com/iot/latest/apireference/API_UpdateIndexingConfiguration.html) API
- Keyed by **thing name**, so a client with no thing cannot be looked up.
- Use this instead of `GetConnection` when the disconnect is older than 30 minutes.

```sh
~$ aws iot get-indexing-configuration
{
    "thingIndexingConfiguration": {
        "thingIndexingMode": "OFF",
        "thingConnectivityIndexingMode": "OFF",
        "deviceDefenderIndexingMode": "OFF",
        "namedShadowIndexingMode": "OFF",
        "filter": {}
    },
    "thingGroupIndexingConfiguration": {
        "thingGroupIndexingMode": "OFF"
    }
}
~$ aws iot update-indexing-configuration \
  --thing-indexing-configuration "thingIndexingMode=REGISTRY_AND_SHADOW,thingConnectivityIndexingMode=STATUS"
~$ aws iot get-indexing-configuration
~$ aws iot get-thing-connectivity-data --thing-name <thingName>
```

# 3. Fleet indexing search.

```sh
aws iot search-index \
  --index-name "AWS_Things" \
  --query-string "thingName:<thingName>"
```

`connectivity.connected:true` or `false`

# 4. Lifecycle events

- `$aws/events/presence/connected/+`
- `$aws/events/presence/disconnected/+`

# 5. LWT (Last Will Testament)

LWT ---> non reserved topic ---> IoT Core rule ---> republish action ---> `$aws/things/<thingName>/shadow/name/<shadowName>/update` reserved topic.
LWT can't be published directly to reserved topic, so we need proxy to pass through data.

# 6. IoT logging V2

`AWSIotLogsV2` CloudWatch Log Group

https://docs.aws.amazon.com/iot/latest/developerguide/cloud-watch-logs.html

Log entries

https://docs.aws.amazon.com/iot/latest/developerguide/cwl-format.html

# 7. CloudWatch metrics

account and region aggregates only.

# 8. Shadow flag written from LWT or lifecycle events

# 9. Application level heartbeat.
