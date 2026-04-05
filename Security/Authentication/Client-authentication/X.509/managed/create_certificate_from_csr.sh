#!/usr/bin/env bash

# https://docs.aws.amazon.com/iot/latest/developerguide/device-certs-create.html

CURRENT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
mkdir -p ${CURRENT_DIR}/certificates && cd ${CURRENT_DIR}/certificates

# Generate a private key
openssl genrsa -out device_cert_key_filename.key 2048
# Generate the CSR
openssl req -new \
    -key device_cert_key_filename.key \
    -out device_cert_csr_filename.csr
aws iot create-certificate-from-csr \
    --certificate-signing-request file://device_cert_csr_filename.csr \
    --certificate-pem-outfile device.crt \
    --set-as-active \
    --query certificatePem \
    --output text > device_cert_filename.pem

#####################################################
# AmazonRootCA1.pem
#####################################################
curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Finished
cd ${CURRENT_DIR}
