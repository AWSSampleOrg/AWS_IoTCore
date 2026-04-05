https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html#mqtt-retain

## 1. Message Expiry

### MQTT v3.1.1

Retained messages never expire. They remain on the broker indefinitely until they are either replaced by a new retained message on the same topic or deleted by a client publishing a message with a 0-byte payload

### MQTT v5

Introduces the Message Expiry Interval property. A publisher can set a lifetime (in seconds) for a message. If this interval passes, the broker deletes the retained message, and new subscribers will not receive it upon subscription

## 2. Retain Handling (Subscription Options)

### MQTT 5 allows a client to decide whether it wants to receive retained messages at the time of subscription through Retain Handling options in the SUBSCRIBE packet.

• 0 (Send on subscribe): The broker sends the retained message as soon as the client subscribes (this is the only behavior available in MQTT 3.1.1).
• 1 (Send if new subscription): The broker only sends the retained message if the subscription does not already exist for that session. This prevents redundant messages during reconnections where the subscription might still be active.
• 2 (Do not send): The broker does not send any retained messages upon subscription. This is useful for clients that only want to receive future updates and do not care about the initial state

3. Retain As Published
   • MQTT 3.1.1: When the broker delivers a retained message to a new subscriber, it always sets the RETAIN flag to 1. For established subscriptions, it sets the flag to 0 regardless of how the message was originally published.
   • MQTT 5: Provides a Retain As Published option. If set to 1, the broker forwards the message to the subscriber with the exact RETAIN flag it was published with. This is particularly helpful for "bridge" applications that move messages between multiple brokers while maintaining their original metadata.

4. Broker Capability Discovery
   • MQTT 5 adds a mechanism for the broker to inform clients if it supports retained messages at all. If the broker sets Retain Available to 0 in the CONNACK packet, the client is prohibited from sending any message with the RETAIN flag set to 1.
   • If a client attempts to publish a retained message to a broker that does not support them, the broker can now return a specific Reason Code (0x9A - Retain not supported).

5. Interaction with Shared Subscriptions
   In both versions, shared subscriptions behave differently with retained messages. In MQTT 5, if a message is published with the RETAIN flag set to 1 on a topic that has shared subscribers, the message is delivered to the shared subscribers like any other normal message, but the broker does not send existing retained messages when a new member joins a shared subscription group.

# AWS IoT Device SDK

## V3

```py
mqtt_connection.publish(
    topic=TOPIC,
    payload=data,
    qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
    retain=True
)
```

If True, the server will store the message and its QoS so that it can be delivered to future subscribers whose subscriptions match its topic name.

## V5

```py
mqtt_connection.publish(
    publish_packet=mqtt5.PublishPacket(
        topic=TOPIC,
        payload=data,
        qos=mqtt5.QoS.AT_LEAST_ONCE,
        retain=True
    )
)
```
