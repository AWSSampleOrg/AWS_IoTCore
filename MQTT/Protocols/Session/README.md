# MQTT 3.1.1: Clean Session

In MQTT 3.1.1, session persistence is controlled entirely by the cleanSession flag in the CONNECT packet.

- cleanSession = 1 (Clean Session): The broker and client discard any previous session state and start a new one. This session lasts only as long as the network connection is active; no state data is stored once the client disconnects.

- cleanSession = 0 (Persistent Session): The broker attempts to resume a session associated with the client ID. If no session exists, it creates a new one. After the client disconnects, the broker stores the session state (subscriptions and unacknowledged messages) so they are available when the client reconnects.

**Session duration is controlled by the broker's global settings (e.g., 1 hour in AWS)**

# MQTT 5.0: Clean Start and Session Expiry

MQTT 5.0 splits this functionality into two separate mechanisms to provide greater flexibility: the Clean Start flag and the Session Expiry Interval property.

## Clean Start: This flag controls the beginning of the session.

- Clean Start = 1: The broker terminates any existing session and creates a brand-new one.
- Clean Start = 0: The broker resumes the existing session if one is available for that client ID; otherwise, it creates a new one.

## Session Expiry Interval: This property, sent in the CONNECT or DISCONNECT packets, controls the end of the session by specifying how many seconds a session should persist after a disconnect.

- Interval = 0 (or absent): The session ends immediately when the network connection is closed.
- Interval > 0: The session state is stored for the specified number of seconds.
- Interval = 0xFFFFFFFF: The session never expires.

# Key Differences and Equivalencies

- Direct Comparison: An MQTT 3.1.1 "clean session" is equivalent to MQTT 5.0 with Clean Start = 1 and Session Expiry Interval = 0. An MQTT 3.1.1 "persistent session" is equivalent to MQTT 5.0 with Clean Start = 0 and a Session Expiry Interval > 0.
- Stored State: Persistent sessions in both versions store the client's subscriptions and any unacknowledged QoS 1 or QoS 2 messages. MQTT 5.0 also stores the Will Delay Interval and any Subscription Identifiers.
- Resuming Sessions: In both versions, clients use the sessionPresent flag in the CONNACK message to determine if the broker successfully resumed a previous session. If sessionPresent is 1, the client does not need to resubscribe.
- Cross-Version Compatibility: Resuming sessions across different MQTT versions is not supported; an MQTT 3 session cannot be resumed as an MQTT 5 session, or vice versa.
- Dynamic Changes: Unlike MQTT 3.1.1, MQTT 5.0 allows a client to modify the Session Expiry Interval when it sends a DISCONNECT packet, providing more granular control over how long the broker should keep its data.

| Feature               | MQTT v3.1.1                                                      | MQTT v5.0                                                      |
| --------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------- |
| Persistence Parameter | cleanSession (Flag)                                              | Clean Start (Flag) and Session Expiry Interval (Property)      |
| Duration Control      | Controlled by the broker's global settings (e.g., 1 hour in AWS) | Controlled by the client per session (in seconds)              |
| Dynamic Modification  | Cannot be changed after the connection is established            | Can be modified by the client when sending a DISCONNECT packet |
|                       |                                                                  |                                                                |
