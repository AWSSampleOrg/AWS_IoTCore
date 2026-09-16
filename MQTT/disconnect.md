https://docs.aws.amazon.com/iot/latest/developerguide/ota-troubleshooting-fleet-disconnects.html

1. Use `AWSIoTLogsV2` log group
2. Use [lifecycle disconnect event](https://docs.aws.amazon.com/iot/latest/developerguide/life-cycle-events.html#connect-disconnect). Check the `disconnectReason` field there.
