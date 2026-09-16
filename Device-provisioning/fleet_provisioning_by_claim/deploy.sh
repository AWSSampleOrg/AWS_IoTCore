#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

PROJECT_PREFIX='fleet-provisioning'

aws cloudformation deploy \
  --template-file template.yml \
  --stack-name ${1:-fleet-stack} \
  --parameter-overrides ProjectPrefix=${PROJECT_PREFIX} \
  --capabilities CAPABILITY_NAMED_IAM

certificate_arn=$(aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile ${SOURCE_DIR}/certificates/claim.cert.pem \
  --private-key-outfile ${SOURCE_DIR}/certificates/claim.private.key \
  --query certificateArn \
  --output text)

curl https://www.amazontrust.com/repository/AmazonRootCA1.pem -o ${SOURCE_DIR}/certificates/AmazonRootCA1.pem

# Attach to claim policy
aws iot attach-policy \
  --policy-name ${PROJECT_PREFIX}-claim-policy \
  --target ${certificate_arn}
