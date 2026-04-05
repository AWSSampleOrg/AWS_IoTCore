#!/usr/bin/env bash

set -e

CERT_FILE=certificates/certificate_filename.pem
PRIVATE_KEY=certificates/private_filename.key
ROOT_CA=certificates/AmazonRootCA1.pem

ROLE_ALIAS=iot-role-alias-stack-role-alias
THING_NAME=RoleAliasTestThing

echo "Getting credentials provider endpoint..."
ENDPOINT=$(aws iot describe-endpoint \
  --endpoint-type iot:CredentialProvider
  --query endpointAddress \
  --output text
)

echo "Endpoint: $ENDPOINT"
echo "Requesting credentials..."

RESPONSE=$(curl --cert $CERT_FILE \
     --key $PRIVATE_KEY \
     -H "x-amzn-iot-thingname: $THING_NAME" \
     --cacert $ROOT_CA \
     https://$ENDPOINT/role-aliases/$ROLE_ALIAS/credentials)

echo "$RESPONSE"

export AWS_ACCESS_KEY_ID=$(echo $RESPONSE | jq -r '.credentials.accessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $RESPONSE | jq -r '.credentials.secretAccessKey')
export AWS_SESSION_TOKEN=$(echo $RESPONSE | jq -r '.credentials.sessionToken')

aws s3 ls --region $REGION
