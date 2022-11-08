#!/usr/bin/env bash

S3_BUCKET="**S3 Bucket Name Here**"
STACK_NAME="IoT-Core"
# CertificateId of AWS IoT Core
CERTIFICATE_ID="**CERTIFICATEID**"

aws cloudformation package \
    --template-file template.yml \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged_template.yml

aws cloudformation deploy \
    --template-file packaged_template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        CertificateId=${CERTIFICATE_ID} \
    --capabilities CAPABILITY_NAMED_IAM
