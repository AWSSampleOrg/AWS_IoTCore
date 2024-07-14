#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)
cd ${SOURCE_DIR}

response=$(aws iot create-provisioning-claim --template-name FleetProvisioningTemplate)

certificate_pem=$(echo $response | jq -r .certificatePem)
public_key=$(echo $response | jq -r .keyPair.PublicKey)
private_key=$(echo $response | jq -r .keyPair.PrivateKey)

directory=tmp
mkdir -p $directory
echo -e "${certificate_pem}" >$directory/cert.pem
echo -e "${public_key}" >$directory/public.key
echo -e "${private_key}" >$directory/private.key

endpoint=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)
python fleetprovisioning.py --endpoint $endpoint \
    --cert ${SOURCE_DIR}/$directory/cert.pem \
    --key ${SOURCE_DIR}/$directory/private.key \
    --template_name FleetProvisioningTemplate \
    --template_parameters '{"ThingName": "thing1", "SerialNumber": "1", "DeviceLocation": "Seattle"}'
