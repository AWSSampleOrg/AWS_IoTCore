#!/usr/bin/env bash

STACK_NAME='iot-role-alias-stack'
CERTIFICATE_ARN=''

aws cloudformation deploy \
  --template-file template.yml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    CertificateArn=$CERTIFICATE_ARN
