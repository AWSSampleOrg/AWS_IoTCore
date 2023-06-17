#!/usr/bin/env bash

S3_BUCKET="**S3 Bucket Name Here**"
STACK_NAME="IoT-Core"
# CertificateId of AWS IoT Core
# X.509 certificates authenticate device and client connections. Certificates must be registered with AWS IoT and activated before a device or client can communicate with AWS IoT.
CLIENT_CERTIFICATE_ID=$1

aws cloudformation package \
    --template-file template.yml \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged_template.yml

aws cloudformation deploy \
    --template-file packaged_template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        CertificateId=${CLIENT_CERTIFICATE_ID} \
    --capabilities CAPABILITY_NAMED_IAM
