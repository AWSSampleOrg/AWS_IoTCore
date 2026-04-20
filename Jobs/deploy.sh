#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

STACK_NAME="IoT-Core-Job"
CERTIFICATE_ARN=''

aws cloudformation deploy \
    --template-file template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
    ProjectPrefix="" \
    CertificateArn="${CERTIFICATE_ARN}" \
    --capabilities CAPABILITY_NAMED_IAM

if [ $? -eq 0 ] ; then
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --query 'Stacks[0].Outputs'
fi
