# Session, queuing and retain: decision flows

One PUBLISH can enter two independent stores. That split is the only thing the two MQTT versions share here.

```mermaid
flowchart TD
    PUB["PUBLISH"]
    PUB -->|"RETAIN = 1"| RET["per-TOPIC store<br/>last message only<br/>publisher decides<br/>FLOW B"]
    PUB -->|"matches a subscription of an<br/>offline persistent session"| SES["per-SESSION queue<br/>every matching QoS 1 message<br/>subscriber decides<br/>FLOW A"]
```

## FLOW A + B - how many times is a retained PUBLISH received ?

```mermaid
flowchart TD
    PUB["PUBLISH with RETAIN = 1"]
    TWICE["received TWICE, same payload<br/>first: normal delivery, live or on CONNECT, RETAIN = 0<br/>then: from the topic store on SUBSCRIBE, RETAIN = 1"]
    ONEA["received once<br/>normal delivery, live or on CONNECT<br/>RETAIN = 0"]
    ONEB["received once<br/>from the topic store on SUBSCRIBE<br/>RETAIN = 1"]
    NEVER["never received"]
    PUB --> N{"subscriber at the<br/>moment of PUBLISH?"}
    N -->|"online, subscribed with a<br/>matching filter, wildcard included"| LIVE["normal delivery, live<br/>RETAIN = 0"]
    N -->|"offline"| A{"FLOW A<br/>DELIVERED from the session queue?"}
    N -->|"no matching subscription"| NO1["no normal delivery"]
    A -->|Yes| QUEUED["normal delivery on CONNECT<br/>from the session queue<br/>sessionPresent = 1, RETAIN = 0"]
    A -->|"No, e.g. cleanSession = 1,<br/>or QoS 0 on either side"| NO1
    LIVE --> BA{"FLOW B<br/>DELIVERED from the topic store<br/>on a later SUBSCRIBE?"}
    QUEUED --> BA
    NO1 --> BN{"FLOW B<br/>DELIVERED from the topic store<br/>on a later SUBSCRIBE?"}
    BA -->|Yes| TWICE
    BA -->|"No, e.g. no SUBSCRIBE afterwards,<br/>or a wildcard / $share filter"| ONEA
    BN -->|Yes| ONEB
    BN -->|"No, e.g. no SUBSCRIBE afterwards,<br/>or a wildcard / $share filter"| NEVER
    TWICE -.->|"to receive once: do not SUBSCRIBE again<br/>to a filter that is already active,<br/>e.g. skip it when sessionPresent = 1<br/>MQTT 5 Retain Handling is ignored"| ONEA
    classDef ok fill:#dcedc8,stroke:#33691e,color:#1b2a0a
    classDef warn fill:#fff3c4,stroke:#f57f17,color:#3a2a00
    classDef bad fill:#ffcdd2,stroke:#b71c1c,color:#3a0a0a
    class ONEA,ONEB ok
    class TWICE warn
    class NEVER bad
```

# MQTT 3.1.1

## FLOW A - does a device get what it missed while offline?

```mermaid
flowchart TD
    NOAUTH["CONNECT is not authorized<br/>no persistent session at all"]
    NQ["never queued"]
    DISC["discarded on expiry"]
    WIPE["queue existed, wiped by<br/>your own CONNECT"]
    OK["DELIVERED<br/>sessionPresent = 1<br/>subscriptions reinstated<br/>replay max 10 msg/s"]
    A0{"IAM policy allows iot:Connect with<br/>connectAttributes PersistentConnect?"} -->|No| NOAUTH
    A0 -->|Yes| A1
    A1{"CONNECT #1<br/>cleanSession = 0?"} -->|No| NQ
    A1 -->|Yes| A2
    A2{"SUBSCRIBE<br/>to that topic, with QoS 1?"} -->|No| NQ
    A2 -->|Yes| DC["DISCONNECT<br/>the session persists"]
    DC --> A3
    A3{"ANOTHER client or service PUBLISHes<br/>to that topic while this one is offline,<br/>with QoS 1?"} -->|No| NQ
    A3 -->|Yes| A4
    A4{"reconnects before<br/>session expiry?"} -->|No| DISC
    A4 -->|Yes| A5
    A5{"CONNECT #2<br/>cleanSession = 0?"} -->|No| WIPE
    A5 -->|Yes| OK
    classDef ok fill:#dcedc8,stroke:#33691e,color:#1b2a0a
    classDef bad fill:#ffcdd2,stroke:#b71c1c,color:#3a0a0a
    class OK ok
    class NOAUTH,NQ,DISC,WIPE bad
```

```
persistent connect   authorization, not just the flag: the default policy is a
                     non-persistent connection that passes no attributes, so the policy
                     must permit PersistentConnect through the iot:ConnectAttributes
                     condition key on iot:Connect. That the CONNECT is refused without it
                     follows from the condition-key mechanics; the docs state only the
                     requirement
```

cleanSession is one flag doing both jobs, so the CONNECT #1 and CONNECT #2 checks can never disagree in a client that always sends the same value.

## DEADLINE - how long the queue survives the disconnect

v3.1.1 has no expiry concept at all: the OASIS specification defines neither message nor session expiry. Nothing starts at publish time.

```
subscriber   CONNECT #1     SUBSCRIBE         DISCONNECT
             |              |                 |
             |              |                 |<------------------- session expiry -------------------->|
                                                                                                        ^
                                                                                            the only deadline
publisher                                                   PUBLISH
                                                            |   no timer starts here
```

```
session expiry   a client cannot set it in this version. It is the account quota
                 "Persistent session expiry period", 3600 s by default, applied to every
                 session in the account and changed only by an account limit increase.
                 Approximate: runs up to 30 min long, never short
```

## FLOW B - does a client that subscribes later get the last value?

```mermaid
flowchart TD
    NR["nothing retained<br/>any existing retained<br/>message is left untouched"]
    NS["not delivered on subscribe<br/>only subsequent publishes arrive"]
    GONE["gone, a later subscriber gets nothing"]
    OKB["DELIVERED on SUBSCRIBE<br/>with the RETAIN flag set"]
    NSUB["not delivered<br/>a restored subscription<br/>does not trigger it"]
    B1{"ABSOLUTE<br/>PUBLISH carries RETAIN = 1?"} -->|No| NR
    B1 -->|Yes| S["stored as the topic's only retained message<br/>replaces the previous one<br/>no subscriber needs to exist"]
    S --> B0
    B0{"client sends a<br/>SUBSCRIBE packet?"} -->|"No, only resumed a session<br/>with sessionPresent = 1"| NSUB
    B0 -->|Yes| B2
    B2{"still stored when<br/>the SUBSCRIBE arrives?"} -->|"replaced, or deleted by a<br/>0-byte retained publish"| GONE
    B2 -->|Yes| B3
    B3{"does that filter match<br/>the topic EXACTLY?"} -->|"No, wildcard or<br/>$share/... shared"| NS
    B3 -->|Yes| OKB
    classDef ok fill:#dcedc8,stroke:#33691e,color:#1b2a0a
    classDef bad fill:#ffcdd2,stroke:#b71c1c,color:#3a0a0a
    class OKB ok
    class NR,NS,NSUB,GONE bad
```

```
who can receive   any client, including cleanSession = 1 and QoS 0 subscriptions.
                  No session is involved, so it must re-SUBSCRIBE after each reconnect
not allowed       reserved topics cannot be published with RETAIN set
inspect           ListRetainedMessages / GetRetainedMessage.
                  The session queue has no equivalent read API
```

# MQTT 5

## FLOW A - does a device get what it missed while offline?

```mermaid
flowchart TD
    NOAUTH["CONNECT is not authorized<br/>no persistent session at all"]
    NQ["never queued"]
    DISC["discarded on expiry"]
    WIPE["queue existed, wiped by<br/>your own CONNECT"]
    OK["DELIVERED<br/>sessionPresent = 1<br/>subscriptions reinstated<br/>replay max 10 msg/s"]
    A0{"IAM policy allows iot:Connect with<br/>connectAttributes PersistentConnect?"} -->|No| NOAUTH
    A0 -->|Yes| A1
    A1{"CONNECT #1<br/>Session Expiry Interval > 0?"} -->|"No, or SEI absent"| NQ
    A1 -->|Yes| A2
    A2{"SUBSCRIBE<br/>to that topic, with QoS 1?"} -->|No| NQ
    A2 -->|Yes| DC["DISCONNECT<br/>the session persists"]
    DC --> A3
    A3{"ANOTHER client or service PUBLISHes<br/>to that topic while this one is offline,<br/>with QoS 1?"} -->|No| NQ
    A3 -->|Yes| A4
    A4{"reconnects before<br/>min of session expiry and MEI?"} -->|No| DISC
    A4 -->|Yes| A5
    A5{"CONNECT #2<br/>Clean Start = 0?"} -->|No| WIPE
    A5 -->|Yes| OK
    classDef ok fill:#dcedc8,stroke:#33691e,color:#1b2a0a
    classDef bad fill:#ffcdd2,stroke:#b71c1c,color:#3a0a0a
    class OK ok
    class NOAUTH,NQ,DISC,WIPE bad
```

```
persistent connect   authorization, not just the flag: the default policy is a
                     non-persistent connection that passes no attributes, so the policy
                     must permit PersistentConnect through the iot:ConnectAttributes
                     condition key on iot:Connect. That the CONNECT is refused without it
                     follows from the condition-key mechanics; the docs state only the
                     requirement
```

Clean Start and SEI are separate flags, which is why the two CONNECT checks are independent here: Clean Start = 1 on the first CONNECT does not stop SEI > 0 from holding, yet Clean Start = 1 on the reconnect destroys the queue.

```
Clean Start   ends the PREVIOUS session       -> matters only at the reconnect
SEI           ends the CONNECTING session     -> matters at the first CONNECT,
                                                 and sets the deadline
SEI on DISCONNECT   current SEI = 0   -> cannot be raised above 0
                    current SEI > 0   -> setting 0 ends the session at that DISCONNECT
                    otherwise         -> updates the current session's SEI
```

## DEADLINE - how long the queue survives, the earlier of two timers

```
subscriber   CONNECT #1     SUBSCRIBE         DISCONNECT
             |              |                 |
             |              |                 |<------------------- session expiry -------------------->|
publisher                                                   PUBLISH
                                                            |
                                                            |<---------- MEI ---------->|
                                                                                        ^
                                                                       deadline = whichever elapses first
```

```
session expiry   the client sets it per session through SEI, and it is clamped to
                 the same account quota "Persistent session expiry period" as MQTT 3,
                 3600 s by default with up to 7 days supported. The clamped value comes
                 back in the CONNACK. Approximate: runs up to 30 min long, never short
MEI              v5 only, PUBLISH property, v5 spec 3.3.2.3.3. min 1 s, a client-sent 0
                 is adjusted to 1, max 604800 s and higher values are clamped. Absent
                 means never expires. Only shortens retention, never extends it past
                 session expiry. Outbound the subscriber sees the remaining interval,
                 and 999 ms or less reads as 0
```

## FLOW B - does a client that subscribes later get the last value?

```mermaid
flowchart TD
    NR["nothing retained<br/>any existing retained<br/>message is left untouched"]
    NS["not delivered on subscribe<br/>only subsequent publishes arrive"]
    GONE["gone, a later subscriber gets nothing"]
    OKB["DELIVERED on SUBSCRIBE<br/>with the RETAIN flag set"]
    NSUB["not delivered<br/>a restored subscription<br/>does not trigger it"]
    B1{"ABSOLUTE<br/>PUBLISH carries RETAIN = 1?"} -->|No| NR
    B1 -->|Yes| S["stored as the topic's only retained message<br/>replaces the previous one<br/>no subscriber needs to exist"]
    S --> B0
    B0{"client sends a<br/>SUBSCRIBE packet?"} -->|"No, only resumed a session<br/>with sessionPresent = 1"| NSUB
    B0 -->|Yes| B2
    B2{"still stored when<br/>the SUBSCRIBE arrives?"} -->|"MEI elapsed"| GONE
    B2 -->|"replaced, or deleted by a<br/>0-byte retained publish"| GONE
    B2 -->|Yes| B3
    B3{"does that filter match<br/>the topic EXACTLY?"} -->|"No, wildcard or<br/>$share/... shared"| NS
    B3 -->|Yes| OKB
    classDef ok fill:#dcedc8,stroke:#33691e,color:#1b2a0a
    classDef bad fill:#ffcdd2,stroke:#b71c1c,color:#3a0a0a
    class OKB ok
    class NR,NS,NSUB,GONE bad
```

```
who can receive   any client, including Clean Start = 1 and QoS 0 subscriptions.
                  No session is involved, so it must re-SUBSCRIBE after each reconnect
not allowed       reserved topics cannot be published with RETAIN set
inspect           ListRetainedMessages / GetRetainedMessage.
                  The session queue has no equivalent read API
```

# Cross-version

```
sessions   never resumable across versions: an MQTT 3 session cannot be resumed as
           MQTT 5, or vice versa, whatever the flags
MEI        decided by the MQTT version of the INBOUND publish, not the subscriber's.
           An MQTT 5 publisher's MEI can expire a message queued for an MQTT 3
           subscriber. MQTT 3 cannot set an MEI but can lose a message to one
```

Sources: [MQTT](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html) and [AWS IoT Core quotas](https://docs.aws.amazon.com/general/latest/gr/iot-core.html) in the AWS IoT Core developer guide, plus the OASIS [MQTT v3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html) and [MQTT v5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html) specifications.
