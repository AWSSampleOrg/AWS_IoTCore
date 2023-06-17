#!/usr/bin/env bash

S3_BUCKET=$1
echo "S3_BUCKET to store Lambda source codes: ${S3_BUCKET}"

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)

rm -r ${SOURCE_DIR}/certificates/output

cd ${SOURCE_DIR}
. certificates/ca_cli.sh
cd ${SOURCE_DIR}
. certificates/client_cli.sh
cd ${SOURCE_DIR}
. deploy.sh $1

curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem

# cpp
cp -r ${SOURCE_DIR}/certificates/output/ ${SOURCE_DIR}/Device/cpp/src/certificates
cp AmazonRootCA1.pem ${SOURCE_DIR}/Device/cpp/src/certificates
# python
cp -r ${SOURCE_DIR}/certificates/output/ ${SOURCE_DIR}/Device/python/src/certificates
cp AmazonRootCA1.pem ${SOURCE_DIR}/Device/python/src/certificates

rm AmazonRootCA1.pem
