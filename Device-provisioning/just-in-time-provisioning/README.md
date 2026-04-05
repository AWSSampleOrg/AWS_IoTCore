# JITP Setup

## 1. Deploy Stack

```bash
./deploy.sh
```

Creates: Thing Type, Thing Group, IoT Policy, Provisioning Role, Provisioning Template

## 2. Create Certificates

```bash
cd ../../Security/Authentication/Client-authentication/X.509/own
. ca_default.sh
```

Save the CA ARN from the output

```bash
. client.sh
cd -
```

## 3. Link CA to Provisioning Template

```bash
aws iot update-ca-certificate \
  --certificate-id <CA_ARN_FROM_STEP_2> \
  --new-auto-registration-status ENABLE \
  --registration-config templateName=jitp-template
```

## 4. Copy Certificates

```bash
mkdir -p iot_client/certificates
cp ../../Security/Authentication/Client-authentication/X.509/own/certificates/device_cert_filename.pem \
   iot_client/certificates/device.cert.pem
cp ../../Security/Authentication/Client-authentication/X.509/own/certificates/device_cert_key_filename.key \
   iot_client/certificates/device.private.key
cp ../../Security/Authentication/Client-authentication/X.509/own/certificates/AmazonRootCA1.pem \
   iot_client/certificates/AmazonRootCA1.pem
```

## 5. Run Client

```bash
cd iot_client
python client.py
```

Device connects with CA-signed cert → automatic provisioning
