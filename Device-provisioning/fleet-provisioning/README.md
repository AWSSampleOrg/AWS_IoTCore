# Fleet Provisioning

AWS IoT Fleet Provisioning enables devices to automatically provision themselves with unique certificates and register as Things in IoT Core.

## Overview

Fleet provisioning uses a shared **claim certificate** for initial device onboarding, then creates unique **device certificates** for each device during the provisioning process.

## Architecture

```
Device (Claim Cert) → IoT Core → Provisioning Template → Lambda Hook → Create Thing + Device Cert
```

## Policies

### ClaimPolicy
- **Purpose**: Temporary policy for unprovisioned devices
- **Attached to**: Claim certificate (shared across devices)
- **Permissions**:
  - Connect to IoT Core
  - Publish/Subscribe to `$aws/certificates/create/*`
  - Publish/Subscribe to `$aws/provisioning-templates/FleetProvisioningTemplate/provision/*`
- **Usage**: Only during provisioning process

### DevicePolicy
- **Purpose**: Permanent policy for provisioned devices
- **Attached to**: Unique device certificate (created during provisioning)
- **Permissions**:
  - Connect to IoT Core
  - Publish/Receive on all topics
  - Subscribe to all topic filters
- **Usage**: Normal device operations after provisioning

## IoT Core API Flow

### Phase 1: Initial Connection
```
Device establishes MQTT connection using claim certificate
├─ Authenticates with X.509 claim certificate
├─ ClaimPolicy evaluated
└─ Connection established
```

### Phase 2: CreateKeysAndCertificate
```
Device → IoT Core: CreateKeysAndCertificate (via MQTT)
├─ Subscribe: $aws/certificates/create/json/accepted
├─ Subscribe: $aws/certificates/create/json/rejected
├─ Publish: $aws/certificates/create/json {}
└─ Response: {
    certificateId,
    certificatePem,
    privateKey,
    certificateOwnershipToken
  }

IoT Core API: CreateKeysAndCertificate
├─ Generates new X.509 certificate
├─ Generates private key
├─ Certificate status: INACTIVE
└─ Returns ownership token
```

### Phase 3: RegisterThing
```
Device → IoT Core: RegisterThing (via MQTT)
├─ Subscribe: $aws/provisioning-templates/{template}/provision/json/accepted
├─ Subscribe: $aws/provisioning-templates/{template}/provision/json/rejected
├─ Publish: $aws/provisioning-templates/{template}/provision/json
│   {
│     certificateOwnershipToken,
│     parameters: { DeviceId }
│   }
└─ Response: {
    deviceConfiguration,
    thingName
  }

IoT Core executes:
├─ (Optional) Lambda:Invoke PreProvisioningHook
│   ├─ Input: { parameters, certificateId }
│   └─ Output: { allowProvisioning, parameterOverrides }
│
├─ CreateThing
│   └─ ThingName: "MyDevice-{DeviceId}"
│
├─ UpdateCertificate
│   └─ Status: ACTIVE
│
├─ AttachPolicy
│   ├─ PolicyName: DevicePolicy
│   └─ Target: new certificate
│
└─ AttachThingPrincipal
    ├─ ThingName: "MyDevice-{DeviceId}"
    └─ Principal: certificate ARN
```

### Phase 4: Reconnect
```
Device disconnects and reconnects with new certificate
├─ Saves certificatePem → certificate/device-cert.pem
├─ Saves privateKey → certificate/device-private.key
├─ MQTT DISCONNECT (claim connection)
└─ MQTT CONNECT (device certificate)
    ├─ Authenticates with new X.509 certificate
    ├─ DevicePolicy evaluated
    └─ Connection established
```

## IoT Core APIs Used

| API | Triggered By | Purpose |
|-----|--------------|---------|
| `CreateKeysAndCertificate` | Device MQTT publish | Generate unique certificate and private key |
| `RegisterThing` | Device MQTT publish | Create Thing and attach certificate |
| `CreateThing` | RegisterThing | Create Thing resource |
| `UpdateCertificate` | RegisterThing | Activate certificate |
| `AttachPolicy` | RegisterThing | Attach DevicePolicy to certificate |
| `AttachThingPrincipal` | RegisterThing | Link certificate to Thing |
| `Lambda:Invoke` | RegisterThing (optional) | Pre-provisioning validation |

## CloudFormation Resources

- **ProvisioningTemplate**: Defines Thing creation template with DeviceId parameter
- **ClaimPolicy**: Policy for claim certificate (fleet provisioning topics only)
- **DevicePolicy**: Policy for provisioned device certificates (full IoT operations)
- **PolicyPrincipalAttachment**: Attaches ClaimPolicy to claim certificate
- **ProvisioningRole**: IAM role for IoT to create Things and certificates

## Usage

1. Deploy CloudFormation template with claim certificate ARN
2. Place claim certificate and private key in `certificate/` directory
3. Run `python client.py`
4. Device provisions itself and saves new certificate to `certificate/device-cert.pem`

## Files

- `client.py`: Main provisioning client
- `mqtt_client_wrapper.py`: MQTT connection management
- `iotidentity_wrapper.py`: Fleet provisioning API calls
- `template.yml`: CloudFormation template
