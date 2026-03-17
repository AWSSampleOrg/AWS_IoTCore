## MQTT v3.1.1

| QoS | Clean Session         | Retained Flag | Device Status          | Reconnect Time | Message Retention | Behavior                                     | Notes |
| --- | --------------------- | ------------- | ---------------------- | -------------- | ----------------- | -------------------------------------------- | ----- |
| 0   | false (persistent)    | false         | Connected              | N/A            | N/A               | [1]                                          | [6]   |
| 0   | false (persistent)    | false         | Disconnected           | N/A            | N/A               | [2]                                          | [6]   |
| 0   | false (persistent)    | true          | Connected              | N/A            | N/A               | [1], retained msg stored                     | [6]   |
| 0   | false (persistent)    | true          | Disconnected           | N/A            | N/A               | [2], retained msg stored                     | [6]   |
| 0   | true (non-persistent) | false         | Connected              | N/A            | N/A               | [1]                                          | [7]   |
| 0   | true (non-persistent) | false         | Disconnected           | N/A            | N/A               | [2]                                          | [7]   |
| 1   | false (persistent)    | false         | Connected              | N/A            | N/A               | [3]                                          | [8]   |
| 1   | false (persistent)    | false         | Disconnected           | < 1 hour       | Up to 1 hour      | [4], delivered on reconnect                  | [8]   |
| 1   | false (persistent)    | false         | Disconnected           | > 1 hour       | Up to 1 hour      | [4], messages discarded after 1 hour         | [8]   |
| 1   | false (persistent)    | true          | Connected              | N/A            | N/A               | [3], retained msg stored                     | [8]   |
| 1   | false (persistent)    | true          | Disconnected           | < 1 hour       | Up to 1 hour      | [4], delivered on reconnect, retained stored | [8]   |
| 1   | true (non-persistent) | false         | Connected              | N/A            | N/A               | [3]                                          | [9]   |
| 1   | true (non-persistent) | false         | Disconnected           | N/A            | N/A               | [2]                                          | [9]   |
| 2   | false (persistent)    | false         | Connected/Disconnected | N/A            | N/A               | N/A                                          | [10]  |
| 2   | true (non-persistent) | false         | Connected/Disconnected | N/A            | N/A               | N/A                                          | [10]  |

**Explanations:**

1. Delivered immediately, no acknowledgment
2. Not queued - messages lost
3. Delivered with acknowledgment
4. Queued by broker
5. Stored by broker, delivered to new subscribers (no expiry in v3)
6. QoS 0 = "fire and forget", no queuing even with persistent session
7. QoS 0 never queues messages
8. Messages queued until device reconnects or 1 hour expires
9. QoS 1 guarantees delivery only while connected
10. QoS 2 not supported by AWS IoT Core

## MQTT v5

| QoS | Clean Start | Session Expiry Interval | Message Expiry Interval | Retained Flag | Device Status          | Reconnect Time      | Message Retention        | Behavior                                           | Notes |
| --- | ----------- | ----------------------- | ----------------------- | ------------- | ---------------------- | ------------------- | ------------------------ | -------------------------------------------------- | ----- |
| 0   | true        | 0 (no session)          | Not set                 | false         | Connected              | N/A                 | N/A                      | [1]                                                | [7]   |
| 0   | true        | 0 (no session)          | Not set                 | false         | Disconnected           | N/A                 | N/A                      | [2]                                                | [7]   |
| 0   | true        | 0 (no session)          | Not set                 | true          | Connected              | N/A                 | N/A                      | [1], retained msg stored with expiry               | [7]   |
| 0   | false       | 3600 (1 hour)           | Not set                 | false         | Connected              | N/A                 | N/A                      | [1]                                                | [13]  |
| 0   | false       | 3600 (1 hour)           | Not set                 | false         | Disconnected           | N/A                 | N/A                      | [2]                                                | [13]  |
| 1   | true        | 0 (no session)          | Not set                 | false         | Connected              | N/A                 | N/A                      | [3]                                                | [14]  |
| 1   | true        | 0 (no session)          | Not set                 | false         | Disconnected           | N/A                 | N/A                      | [2]                                                | [14]  |
| 1   | false       | 3600 (1 hour)           | Not set                 | false         | Connected              | N/A                 | N/A                      | [3]                                                | [17]  |
| 1   | false       | 3600 (1 hour)           | Not set                 | false         | Disconnected           | < 1 hour            | Up to 1 hour             | [4], delivered on reconnect                        | [17]  |
| 1   | false       | 3600 (1 hour)           | Not set                 | false         | Disconnected           | > 1 hour            | Up to 1 hour             | [4], messages discarded after 1 hour               | [17]  |
| 1   | false       | 3600 (1 hour)           | 1800 (30 min)           | false         | Disconnected           | < 30 min            | Up to 30 min (MEI)       | [4], delivered on reconnect before MEI expires     | [18]  |
| 1   | false       | 3600 (1 hour)           | 1800 (30 min)           | false         | Disconnected           | > 30 min, < 1 hour  | Up to 30 min (MEI)       | [4], messages discarded after 30 min (MEI expired) | [18]  |
| 1   | false       | 7200 (2 hours)          | Not set                 | false         | Disconnected           | < 1 hour            | Up to 1 hour (AWS limit) | [4], delivered on reconnect                        | [19]  |
| 1   | false       | 7200 (2 hours)          | Not set                 | false         | Disconnected           | > 1 hour, < 2 hours | Up to 1 hour (AWS limit) | [4], messages discarded after 1 hour (AWS limit)   | [19]  |
| 1   | false       | 3600 (1 hour)           | Not set                 | true          | Disconnected           | < 1 hour            | Up to 1 hour             | [4], delivered on reconnect, retained msg stored   | [17]  |
| 1   | false       | 3600 (1 hour)           | 1800 (30 min)           | true          | Disconnected           | < 30 min            | Up to 30 min (MEI)       | [4], delivered, retained msg respects MEI          | [18]  |
| 2   | true        | 0 (no session)          | Not set                 | false         | Connected/Disconnected | N/A                 | N/A                      | N/A                                                | [10]  |
| 2   | false       | > 0                     | Not set                 | false         | Connected/Disconnected | N/A                 | N/A                      | N/A                                                | [10]  |

**Explanations:**

1. Delivered immediately, no acknowledgment
2. Not queued - messages lost
3. Delivered with acknowledgment
4. Queued by broker
5. Stored by broker, delivered to new subscribers (no expiry in v3)
6. QoS 0 = "fire and forget", no queuing even with persistent session
7. QoS 0 never queues messages
8. Messages queued until device reconnects or 1 hour expires
9. QoS 1 guarantees delivery only while connected
10. QoS 2 not supported by AWS IoT Core
11. Optional (publisher sets)
12. Stored by broker, delivered to new subscribers, respects Message Expiry if set
13. QoS 0 = "fire and forget", no queuing
14. No session = no queuing
15. Optional (publisher sets, broker discards if expired)
16. Whichever is shorter
17. AWS IoT Core enforces 1 hour max regardless of Session Expiry setting
18. Message Expiry Interval (MEI) takes precedence over session expiry for message retention
19. AWS IoT Core enforces 1 hour max for message retention even if Session Expiry is longer

# Key differences in MQTT v5:

- **Clean Start** replaces Clean Session (more flexible)
- **Session Expiry Interval** allows clients to specify how long the session should persist (0 to 4,294,967,295 seconds)
- **Message Expiry Interval** allows publishers to specify how long a message remains valid (in seconds). If set, the broker will discard the message after this interval expires, even if it hasn't been delivered yet. If not set, messages don't expire based on age (only subject to session/retention limits)
- **AWS IoT Core limitation**: Even if Session Expiry Interval is set higher, AWS IoT Core still enforces a 1 hour maximum for message retention
