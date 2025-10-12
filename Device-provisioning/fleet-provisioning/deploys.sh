#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

S3_BUCKET=''

STACK_NAME="IoT-Core-Fleet-Provisioning"

CERTIFICATE_DIR=${SOURCE_DIR}/certificate
mkdir -p ${CERTIFICATE_DIR}

aws iot create-keys-and-certificate \
    --set-as-active \
    --certificate-pem-outfile ${CERTIFICATE_DIR}/claim-cert.pem \
    --public-key-outfile ${CERTIFICATE_DIR}/claim-public.key \
    --private-key-outfile ${CERTIFICATE_DIR}/claim-private.key > ${CERTIFICATE_DIR}/claim-certificate-result.json

aws s3 cp ${CERTIFICATE_DIR}/claim-certificate-result.json s3://$S3_BUCKET/certificates/claim-certificate-result.json


aws cloudformation package \
    --template-file template.yml \
    --s3-bucket ${S3_BUCKET} \
    --output-template-file packaged_template.yml

aws cloudformation deploy \
    --template-file packaged_template.yml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
    ProjectPrefix="" \
    ClientCertificateArn=$(cat ${CERTIFICATE_DIR}/claim-certificate-result.json | jq -r .certificateArn) \
    --capabilities CAPABILITY_NAMED_IAM
