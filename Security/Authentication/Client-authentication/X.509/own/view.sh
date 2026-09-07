#!/usr/bin/env bash

CERTS_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)/certificates

openssl pkey -in ${CERTS_DIR}/device_cert_key_filename.key -text -noout

# Show the only public key in the private key
# openssl pkey -in ${CERTS_DIR}/device_cert_key_filename.key -text -noout -pubout


# Show the root certificate
openssl x509 -in ${CERTS_DIR}/device_cert_filename.pem -text -noout

# CSR
openssl req -in ${CERTS_DIR}/device_cert_csr_filename.csr -text -noout
