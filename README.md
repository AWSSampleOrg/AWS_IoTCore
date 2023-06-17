# AWS IoT Core

(Create CA and X.509 Certificates)[certificates]

# Generate certificates with CLI

1. Create and Register CA certificate with AWS IoT

```sh
. certificates/ca_cli.sh
```

2. Create and Register client certificate with AWS IoT

```sh
. certificates/client_cli.sh
```


# Execute source codes on devices

### cpp

```sh
copy certificates
cd Device/cpp/src
curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem
cp -r ../../../certificates/output/device_cert_filename.pem .
cp -r ../../../certificates/output/device_cert_key_filename.key .
cp -r ../../../certificates/output/root_CA_cert_filename.pem .

# build source code using cmake
cd .. && . build.sh
# execute program
./main
```
