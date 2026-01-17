#!/usr/bin/env bash

# https://docs.aws.amazon.com/iot/latest/developerguide/device-certs-create.html

CURRENT_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
mkdir -p ${CURRENT_DIR}/certificates && cd ${CURRENT_DIR}/certificates

# This command creates private key, public key, and X.509 certificate files and registers and activates the certificate with AWS IoT.
aws iot create-keys-and-certificate \
    --set-as-active \
    --certificate-pem-outfile certificate_filename.pem \
    --public-key-outfile public_filename.key \
    --private-key-outfile private_filename.key

#####################################################
# AmazonRootCA1.pem
#####################################################
curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Finished
cd ${CURRENT_DIR}
