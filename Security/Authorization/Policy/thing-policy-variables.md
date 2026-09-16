# Point of thing policy variables

## 1. You must match your client ID with the thing name. [EXCLUSIVE_THING and NON_EXCLUSIVE_THING](https://docs.aws.amazon.com/iot/latest/developerguide/exclusive-thing.html) don't differ here - exclusive still requires the client ID to equal the thing name.

## 2. The certificate presented must be attached to that thing.

## 3. MQTT over TLS and MQTT over WebSocket only. HTTPS has no client ID, so nothing resolves.

# [Thing policy variables](https://docs.aws.amazon.com/iot/latest/developerguide/thing-policy-variables.html)

```
If you use non-exclusive thing association, the same certificate can be attached to multiple things. To maintain a clear association and to avoid potential conflicts, you must match your client ID with the thing name. In this case, you obtain the thing name from the client ID in the MQTT Connect message sent when a thing connects to AWS IoT Core.

Keep the following in mind when using thing policy variables in AWS IoT Core policies.

    Use the AttachThingPrincipal API to attach certificates or principals (authenticated Amazon Cognito identities) to a thing.

    If non-exclusive thing association is in place, when you're replacing thing names with thing policy variables, the value of clientId in the MQTT connect message or the TLS connection must exactly match the thing name.

The following thing policy variables are available:

    iot:Connection.Thing.ThingName

    This resolves to the name of the thing in the AWS IoT Core registry for which the policy is being evaluated. AWS IoT Core uses the certificate the device presents when it authenticates to determine which thing to use to verify the connection. This policy variable is only available when a device connects over MQTT or MQTT over the WebSocket protocol.

    iot:Connection.Thing.ThingTypeName

    This resolves to the thing type associated with the thing for which the policy is being evaluated. The client ID of the MQTT/WebSocket connection must be the same as the thing name. This policy variable is available only when connecting over MQTT or MQTT over the WebSocket protocol.

    iot:Connection.Thing.Attributes[attributeName]

    This resolves to the value of the specified attribute associated with the thing for which the policy is being evaluated. A thing can have up to 50 attributes. Each attribute is available as a policy variable: iot:Connection.Thing.Attributes[attributeName] where attributeName is the name of the attribute. The client ID of the MQTT/WebSocket connection must be the same as the thing name. This policy variable is only available when connecting over MQTT or MQTT over the WebSocket protocol.

    iot:Connection.Thing.IsAttached

    iot:Connection.Thing.IsAttached: ["true"] enforces that only the devices that are both registered in AWS IoT and attached to principal can access the permissions inside the policy. You can use this variable to prevent a device from connecting to AWS IoT Core if it presents a certificate that is not attached to an IoT thing in the AWS IoT Core registry.This variable has values true or false indicating that the connecting thing is attached to the certificate or Amazon Cognito identity in the registry using AttachThingPrincipal API. Thing name is taken as client Id.

If your client ID matches your thing name, or if you attach your certificate to a thing exclusively, using policy variables in the policy definition can simplify policy management. Instead of creating individual policies for each IoT thing, you can define a single policy using the thing policy variables. This policy can be applied to all devices dynamically. The following is an example policy to show how it works. For more information, see Associating an AWS IoT thing to an MQTT client connection.
```

## iot:Connect

- Both of the statements below do the same thing. They let a device connect only as the thing its own certificate is attached to.
  They get there differently. The first resolves the thing name from the certificate, substitutes it into the resource ARN, and compares that against the client ID being requested - a mismatch means the resource doesn't match.
  The second matches any client ID in the resource and lets the condition do the work, checking the registry for an attachment between the presented certificate and the thing named by the client ID.

- ### Using the policy variable ${iot:ClientId} with Connect is not recommended
  https://docs.aws.amazon.com/iot/latest/developerguide/basic-policy-variables.html
  ```
  There is no check on the value of ClientId, so an attacher with a different client's ID can pass the validation but cause disconnection. Because any ClientId is allowed, setting a random client ID can bypass thing group policies.
  ```

### Either way the client ID must equal the thing name, so a device cannot connect using another device's certificate.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["iot:Connect"],
      "Resource": [
        "arn:aws:iot:us-east-1:123456789012:client/${iot:Connection.Thing.ThingName}"
      ]
    }
  ]
}
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["iot:Connect"],
      "Resource": "arn:aws:iot:us-east-1:123456789012:client/*",
      "Condition": {
        "Bool": {
          "iot:Connection.Thing.IsAttached": ["true"]
        }
      }
    }
  ]
}
```

## iot:Connect, iot:Publish, iot:Receive, iot:Subscribe

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["iot:Connect"],
      "Resource": [
        "arn:aws:iot:us-east-1:123456789012:client/${iot:Connection.Thing.ThingName}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["iot:Publish"],
      "Resource": [
        "arn:aws:iot:us-east-1:123456789012:topic/my/topic/${iot:ClientId}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["iot:Receive"],
      "Resource": [
        "arn:aws:iot:us-east-1:123456789012:topic/my/topic/${iot:ClientId}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["iot:Subscribe"],
      "Resource": [
        "arn:aws:iot:us-east-1:123456789012:topicfilter/my/topic/${iot:ClientId}"
      ]
    }
  ]
}
```
