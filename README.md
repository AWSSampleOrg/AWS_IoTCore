# AWS IoT Core

https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html

- Device gateway
  Serves as the front door for IoT devices, focusing on security, authentication, and translation between edge protocols (e.g., Bluetooth, Modbus, MQTT) and cloud protocols. And publish metrics, Check logging level.

  ```
  Enables devices to securely and efficiently communicate with AWS IoT. Device communication is secured by secure protocols that use X.509 certificates.
  ```

- Message broker
  Sits behind the gateway, serving as the central hub for routing data asynchronously. It manages the pub/sub pattern to distribute messages to applications.

  ```
  Provides a secure mechanism for devices and AWS IoT applications to publish and receive messages from each other. You can use either the MQTT protocol directly or MQTT over WebSocket to publish and subscribe. For more information about the protocols that AWS IoT supports, see Device communication protocols. Devices and clients can also use the HTTP REST interface to publish data to the message broker.

  The message broker distributes device data to devices that have subscribed to it and to other AWS IoT Core services, such as the Device Shadow service and the rules engine.
  ```
