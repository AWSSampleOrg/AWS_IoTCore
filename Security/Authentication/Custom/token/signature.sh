#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

# Whatever value is ok for TOKEN_VALUE
# https://docs.aws.amazon.com/iot/latest/developerguide/custom-auth.html#custom-auth-token-signature
TOKEN_VALUE="my-test-token"
echo -n $TOKEN_VALUE | openssl dgst -sha256 -sign ${SOURCE_DIR}/certificates/id_rsa.key | base64 | tr -d '\n'
