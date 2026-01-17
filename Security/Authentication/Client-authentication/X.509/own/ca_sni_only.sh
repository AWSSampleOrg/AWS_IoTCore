#!/usr/bin/env bash

CURRENT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
mkdir -p ${CURRENT_DIR}/certificates && cd ${CURRENT_DIR}/certificates

# Detail Info
# https://docs.aws.amazon.com/iot/latest/developerguide/manage-your-CA-certs.html

#####################################################
# Create a CA certificate
#####################################################
# 1. Generate a key pair.
openssl genrsa -out root_CA_key_filename.key 2048
# 2. Use the private key from the key pair to generate a CA certificate.
## use v3_ca section in openssl.cnf
openssl req -x509 -new -nodes \
    -key root_CA_key_filename.key \
    -sha256 -days 1024 \
    -out root_CA_cert_filename.pem

#####################################################
# Register a CA certificate in SNI_ONLY mode (CLI)
#####################################################
# 5. Register the CA certificate with AWS IoT. Pass in the CA certificate file name and the private key verification certificate file name to the register-ca-certificate command, as follows. For more information, see register-ca-certificate in the AWS CLI Command Reference.
aws iot register-ca-certificate \
    --ca-certificate file://root_CA_cert_filename.pem \
    --certificate-mode SNI_ONLY \
    --set-as-active

#####################################################
# AmazonRootCA1.pem
#####################################################
curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Finished
cd ${CURRENT_DIR}
