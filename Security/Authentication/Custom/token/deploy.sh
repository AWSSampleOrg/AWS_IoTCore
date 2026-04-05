#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

mkdir -p ${SOURCE_DIR}/certificates && cd ${SOURCE_DIR}/certificates
openssl genrsa -out id_rsa.key 4096
openssl rsa -in id_rsa.key -pubout -out id_rsa.pub
curl -O https://www.amazontrust.com/repository/AmazonRootCA1.pem
cd ${SOURCE_DIR}

S3_BUCKET=''
STACK_NAME="IoT-Core-Custom-Auth-With-Token"

aws cloudformation package \
    --template-file template.yml \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged_template.yml

aws cloudformation deploy \
    --template-file packaged_template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
    ProjectPrefix="" \
    TokenValue="$(cat ${SOURCE_DIR}/certificates/id_rsa.pub)" \
    --capabilities CAPABILITY_NAMED_IAM
