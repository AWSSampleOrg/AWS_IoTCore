# JITR Setup

## 1. Create Certificates

```bash
cd ../../Security/Authentication/Client-authentication/X.509/own
. ca_default.sh
. client.sh
cd -
```

## 2. Copy Certificates

```bash
mkdir -p iot_client/certificates
cp ../../Security/Authentication/Client-authentication/X.509/own/certificates/device_cert_filename.pem \
   iot_client/certificates/device.cert.pem
cp ../../Security/Authentication/Client-authentication/X.509/own/certificates/device_cert_key_filename.key \
   iot_client/certificates/device.private.key
cp ../../Security/Authentication/Client-authentication/X.509/own/certificates/AmazonRootCA1.pem \
   iot_client/certificates/AmazonRootCA1.pem
```

## 3. Deploy Stack

```bash
./deploy.sh
```

## 4. Add Serial Numbers to DynamoDB

```bash
aws dynamodb put-item \
  --table-name jitr-SerialNumbers \
  --item '{"serialNumber": {"S": "12345"}, "Ownership": {"S": "Company1"}}'
```

## 5. Run Client

```bash
cd iot_client
python client.py
```

Device connects with CA-signed cert → Lambda validates → provisions
