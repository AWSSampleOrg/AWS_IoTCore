# Bulk Registration Setup

## 1. Deploy Stack
```bash
./deploy.sh
```

Creates: Thing Type, Thing Group, IoT Policy, S3 Bucket, Provisioning Role

## 2. Generate CSRs
```bash
# For each device
openssl genrsa -out device.key 2048
openssl req -new -key device.key -out device.csr
```

## 3. Create parameters.json
```json
{"ThingName": "Device1", "SerialNumber": "123", "CSR": "-----BEGIN CERTIFICATE REQUEST-----..."}
{"ThingName": "Device2", "SerialNumber": "456", "CSR": "-----BEGIN CERTIFICATE REQUEST-----..."}
```

## 4. Upload and Start Task
```bash
# Upload to S3
aws s3 cp parameters.json s3://bulk-<ACCOUNT_ID>/parameters.json

# Start registration task
aws iot start-thing-registration-task \
  --template-body file://template.json \
  --input-file-bucket bulk-<ACCOUNT_ID> \
  --input-file-key parameters.json \
  --role-arn <ROLE_ARN_FROM_STACK_OUTPUT>
```

## 5. Download Signed Certificates
Check task status and download results from IoT Console

**Certificate Setup**: See `Security/Authentication/Client-authentication/X.509/`
