# JITP Setup

Every time you deploy new thing and its certificate, you need to do step 3 to 5.

## 1. Deploy Stack

```bash
./deploy.sh
```

## 2. Create and register CA certificate

```bash
. ca_default.sh
```

Enable auto registration

```bash
aws iot update-ca-certificate \
  --certificate-id <CA ID> \
  --new-auto-registration-status ENABLE \
  --registration-config templateName=jitp-template
```

## 3. Create client certificate

```sh
. client.sh
```

## 4. Merge device certificate and CA certificate

```sh
cat certificates/device_cert_filename.pem certificates/root_CA_cert_filename.pem > certificates/ca_and_device_certificate.pem
```

## 5. Run Client

Get serial number from certificate. This step is needed due to its logic, not because of JITP

```sh
SERIAL_NUMBER=$(openssl x509 -in certificates/device_cert_filename.pem -noout -serial | cut -d '=' -f 2)
```

```sh
python client.py ${SERIAL_NUMBER}
```

Device connects with CA-signed cert → automatic provisioning
