# AWS IoT Core Device Provisioning Methods

## Overview

AWS IoT Core supports 4 main provisioning methods using X.509 certificates. Each method suits different manufacturing and deployment scenarios.

**All provisioning methods now use CloudFormation templates for infrastructure setup.**

## Deployment

Each provisioning method has:
- `template.yml` - CloudFormation template
- `deploy.sh` - Deployment script
- Simplified client code (no Docker)

### Deploy a Stack

```bash
cd <provisioning-method-directory>
./deploy.sh [stack-name]
```

---

## 1. Just-In-Time Provisioning (JITP)

**Directory**: `just-in-time-provisioning/`

### Deploy
```bash
cd just-in-time-provisioning
./deploy.sh jitp-stack
```

### What It Creates
- Thing Type, Thing Groups, Billing Group
- IoT Policy for devices
- IAM Role for provisioning

### Next Steps
1. Register CA certificate with provisioning template
2. Device connects with CA-signed certificate
3. Automatic provisioning on first connection

---

## 2. Just-In-Time Registration (JITR)

**Directory**: `just-in-time-registration/`

### Deploy
```bash
cd just-in-time-registration
./deploy.sh jitr-stack
```

### What It Creates
- Thing Type, Thing Groups, Billing Group
- IoT Policy for devices
- DynamoDB table for serial number validation
- Lambda function for provisioning logic
- IoT Rule to trigger Lambda

### Next Steps
1. Register CA certificate (without provisioning template)
2. Add authorized serial numbers to DynamoDB
3. Device connects with CA-signed certificate
4. Lambda validates and provisions

---

## 3. Bulk Registration

**Directory**: `bulk-registration-using-csr/`

### Deploy
```bash
cd bulk-registration-using-csr
./deploy.sh bulk-stack
```

### What It Creates
- Thing Types, Thing Groups, Billing Group
- IoT Policy for devices
- S3 bucket for parameters file
- IAM Role for provisioning

### Next Steps
1. Generate CSRs for devices
2. Create parameters.json with device metadata
3. Upload to S3 bucket
4. Start bulk registration task via CLI

---

## 4. Fleet Provisioning by Claim

**Directory**: `fleet_provisioning_by_claim/`

### Deploy
```bash
cd fleet_provisioning_by_claim
./deploy.sh fleet-stack
```

### What It Creates
- Thing Type, Thing Group
- Device policy and Claim policy
- IAM Role for provisioning
- Lambda function for provisioning hook (validation)

### Next Steps
1. Create claim certificate
2. Attach claim policy to certificate
3. Create provisioning template
4. Device requests permanent certificate using claim cert

---

## Common Concepts

### Certificate Authority (CA) Registration
JITP and JITR require a registered CA in AWS IoT Core:
```
1. Generate CA certificate and private key
2. Get registration code from AWS IoT
3. Create verification certificate signed with registration code
4. Register CA with verification certificate
```

### Provisioning Template
JITP, JITR (via Lambda), and Bulk Registration use templates to define resource creation:
- Extract parameters from certificate DN or input file
- Define Thing properties (name, type, groups, attributes)
- Specify certificate activation and policy attachment

---

## 1. Just-In-Time Provisioning (JITP)

### Flow
```
Device (CA-signed cert) 
    ↓
AWS IoT Core (detects unregistered cert from known CA)
    ↓
Provisioning Template (extracts cert DN fields)
    ↓
Resources Created (Thing + activate cert + attach policy)
```

### How It Works
1. Device connects with certificate signed by registered CA
2. AWS IoT auto-registers certificate in PENDING_ACTIVATION
3. Template extracts parameters from certificate DN fields:
   - `AWS::IoT::Certificate::SerialNumber` → ThingName
   - `AWS::IoT::Certificate::CommonName` → Attributes
   - `AWS::IoT::Certificate::OrganizationalUnit` → ThingGroup
4. Resources created automatically, certificate activated

### Key Code
```python
# Device connects with CA-signed certificate
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=endpoint,
    cert_filepath="deviceCert.crt",  # Signed by registered CA
    pri_key_filepath="deviceCert.key"
)
```

**Use Case**: Simple, standardized provisioning with no custom logic needed

---

## 2. Just-In-Time Registration (JITR)

### Flow
```
Device (CA-signed cert)
    ↓
AWS IoT Core (cert registered as PENDING_ACTIVATION)
    ↓
IoT Rule (listens to $aws/events/certificates/registered/+)
    ↓
Lambda Function (validates + provisions)
    ↓
Resources Created (Thing + activate cert + attach policy)
```

### How It Works
1. Device connects with certificate signed by registered CA
2. Certificate auto-registered in PENDING_ACTIVATION state
3. Event published to `$aws/events/certificates/registered/{caCertificateId}`
4. IoT Rule triggers Lambda function with event:
   ```json
   {
     "certificateId": "...",
     "caCertificateId": "...",
     "certificateStatus": "PENDING_ACTIVATION"
   }
   ```
5. Lambda extracts certificate info, validates (e.g., DynamoDB lookup), provisions resources

### Key Code
```python
def lambda_handler(event, context):
    certificate_id = event['certificateId']
    
    # Get certificate details
    response = iot_client.describe_certificate(certificateId=certificate_id)
    cert_pem = response['certificateDescription']['certificatePem']
    
    # Extract serial number using cryptography library
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    serial_number = cert.serial_number
    
    # Validate against DynamoDB
    validation = dynamodb.query(TableName='SerialNumbers', 
                                KeyConditionExpression='serialNumber = :sn')
    
    if validation['Items']:
        # Create Thing
        iot_client.create_thing(thingName=str(serial_number), ...)
        # Activate certificate
        iot_client.update_certificate(certificateId=certificate_id, newStatus='ACTIVE')
        # Attach policy and certificate
        iot_client.attach_policy(policyName='DevicePolicy', target=cert_arn)
        iot_client.attach_thing_principal(thingName=str(serial_number), principal=cert_arn)
```

**Use Case**: Complex validation logic, integration with external systems (databases, APIs)

---

## 3. Bulk Registration

### Flow
```
Generate CSRs (from device private keys)
    ↓
Create parameters.json (device metadata + CSRs)
    ↓
Upload to S3
    ↓
StartThingRegistrationTask API
    ↓
AWS processes batch (signs CSRs, creates resources)
    ↓
Download signed certificates from task results
```

### How It Works
1. Generate private keys and CSRs for each device
2. Create parameters file (one JSON object per line):
   ```json
   {"ThingName": "Device1", "SerialNumber": "123", "CSR": "-----BEGIN CERTIFICATE REQUEST-----..."}
   {"ThingName": "Device2", "SerialNumber": "456", "CSR": "-----BEGIN CERTIFICATE REQUEST-----..."}
   ```
3. Upload to S3 bucket
4. Call API with template and S3 location
5. AWS signs CSRs with Amazon Trust Services CA and provisions resources
6. Download signed certificates from task results

### Key Code
```python
# Generate CSR
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)
req = crypto.X509Req()
req.get_subject().CN = serial_number
req.set_pubkey(key)
req.sign(key, 'sha256')
csr_pem = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)

# Upload and start task
s3_client.upload_file('parameters.json', bucket, 'parameters.json')
iot_client.start_thing_registration_task(
    templateBody=json.dumps(template),
    inputFileBucket=bucket,
    inputFileKey='parameters.json',
    roleArn='arn:aws:iam::account:role/provisioning-role'
)
```

**Use Case**: Batch provisioning of known devices, migrations, large-scale deployments

---

## 4. Fleet Provisioning by Claim

### Flow
```
Device (claim certificate - temporary)
    ↓
CreateKeysAndCertificate (request permanent cert)
    ↓
AWS IoT generates permanent certificate
    ↓
RegisterThing (with template + parameters)
    ↓
[Optional] Provisioning Hook Lambda (validates)
    ↓
Resources Created + permanent cert issued
```

### How It Works
1. Device connects with claim certificate (temporary, restricted policy)
2. Publishes to `$aws/certificates/create/json` to request permanent certificate
3. AWS IoT generates key pair and certificate, returns via `$aws/certificates/create/json/accepted`
4. Device publishes to `$aws/provisioning-templates/{templateName}/provision/json` with:
   - Certificate ownership token
   - Template parameters (SerialNumber, etc.)
5. Optional Lambda hook validates request
6. Resources created, permanent certificate issued
7. Device reconnects with permanent certificate

### Key Code
```python
# Connect with claim certificate
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=endpoint,
    cert_filepath="claim.cert.pem",  # Temporary claim cert
    pri_key_filepath="claim.private.key"
)

# Request permanent certificate
identity_client.publish_create_keys_and_certificate(
    request=iotidentity.CreateKeysAndCertificateRequest(),
    qos=mqtt.QoS.AT_LEAST_ONCE
)

# Register thing with permanent certificate
identity_client.publish_register_thing(
    request=iotidentity.RegisterThingRequest(
        templateName="FleetProvisioningTemplate",
        certificateOwnershipToken=token,
        parameters={"SerialNumber": "12345", "DeviceType": "Sensor"}
    ),
    qos=mqtt.QoS.AT_LEAST_ONCE
)
```

**Provisioning Hook Lambda** (optional):
```python
def lambda_handler(event, context):
    serial_number = event['parameters']['SerialNumber']
    
    # Validate serial number
    if serial_number.startswith("123456"):
        return {
            'allowProvisioning': True,
            'parameterOverrides': {'ThingName': f"Device-{serial_number}"}
        }
    return {'allowProvisioning': False}
```

**Use Case**: Manufacturing without pre-provisioned certificates, dynamic onboarding

---

## Comparison

| Method | Certificate Source | Trigger | Flexibility | Pre-Setup Required |
|--------|-------------------|---------|-------------|-------------------|
| **JITP** | CA-signed (device has before connection) | First connection | Low (template only) | Register CA + template |
| **JITR** | CA-signed (device has before connection) | First connection | High (Lambda) | Register CA + Lambda + IoT Rule |
| **Bulk Registration** | CSR → AWS signs | API call | Medium (batch) | S3 bucket + template |
| **Fleet Provisioning** | AWS generates on-demand | Device request | High (Lambda hook) | Claim cert + template |

## Key Differences

### Certificate Lifecycle
- **JITP/JITR**: Device manufactured with CA-signed certificate
- **Bulk Registration**: Device has private key, CSR signed during registration
- **Fleet Provisioning**: Device gets certificate during provisioning (no pre-cert needed)

### Validation/Authorization
- **JITP**: Certificate DN fields only
- **JITR**: Custom Lambda logic (database, API calls)
- **Bulk Registration**: Pre-approved list in S3
- **Fleet Provisioning**: Claim certificate policy + optional Lambda hook

### When to Use
- **JITP**: Simple use cases, standardized device types, no external validation
- **JITR**: Need to validate against external systems, complex business logic
- **Bulk Registration**: Migrating existing devices, batch onboarding known devices
- **Fleet Provisioning**: Manufacturing line, no certificate pre-provisioning, dynamic parameters

## Complete Flow Comparison

```
JITP:
Device → [CA-signed cert] → AWS IoT → Template → Resources

JITR:
Device → [CA-signed cert] → AWS IoT → Event → IoT Rule → Lambda → Resources

Bulk Registration:
CSRs → S3 → API Call → AWS Batch Process → Resources + Signed Certs

Fleet Provisioning:
Device → [Claim cert] → CreateCert → [Permanent cert] → RegisterThing → [Hook] → Resources
```
