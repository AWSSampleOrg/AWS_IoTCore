#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

S3_BUCKET='your-bucket-name-here'
STACK_NAME="IoT-Core-JobTemplate"

aws cloudformation deploy \
    --template-file template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
    JobTemplateId="$(uuidgen)" \
    BucketName=${S3_BUCKET} \
    --capabilities CAPABILITY_NAMED_IAM
