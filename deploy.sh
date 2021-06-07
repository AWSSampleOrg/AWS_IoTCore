#!/bin/bash
readonly S3_Bucket="**S3 Bucket Name Here**" 2> /dev/null
readonly StackName="IoT-Core" 2> /dev/null
readonly COLOR_RED="\033[31m" 2> /dev/null
readonly COLOR_END="\033[0m" 2> /dev/null

echo "S3_Bucket     : ${S3_Bucket}"
echo "StackName     : ${StackName}"
echo "CertificateId : ${CertificateId}"

# CertificateId of AWS IoT Core
CertificateId=$1
if [ ${CertificateId} = "" ] ; then
    echo -e "${COLOR_RED}Give CertificateId${COLOR_END}"
else
    #package
    aws cloudformation package \
        --template-file template.yml \
        --s3-bucket ${S3_Bucket} \
        --output-template-file packaged_template.yml

    #deploy
    aws cloudformation deploy \
        --template-file packaged_template.yml \
        --stack-name ${StackName} \
        --parameter-overrides \
            CertificateId=${CertificateId} \
        --capabilities CAPABILITY_NAMED_IAM
fi
