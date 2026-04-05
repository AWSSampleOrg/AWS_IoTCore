USER_POOL_ID=
CLIENT_ID=
IDENTITY_POOL_ID=
USER_NAME=
PASSWORD=
AWS_REGION=$(aws configure get region)

ID_TOKEN=$(
    aws cognito-idp admin-initiate-auth \
        --user-pool-id ${USER_POOL_ID} \
        --client-id ${CLIENT_ID} \
        --auth-flow ADMIN_USER_PASSWORD_AUTH \
        --auth-parameters USERNAME=${USER_NAME},PASSWORD=${PASSWORD} \
        --query 'AuthenticationResult.IdToken' \
        --output text
)
IDENTITY_ID=$(
    aws cognito-identity get-id \
        --identity-pool-id ${IDENTITY_POOL_ID} \
        --logins cognito-idp.${AWS_REGION}.amazonaws.com/${USER_POOL_ID}=${ID_TOKEN} \
        --query 'IdentityId' \
        --output text
)
CREDENTIALS=$(
    aws cognito-identity get-credentials-for-identity \
        --identity-id ${IDENTITY_ID} \
        --logins cognito-idp.${AWS_REGION}.amazonaws.com/${USER_POOL_ID}=${ID_TOKEN}
)

SESSION_TOKEN=$(echo ${CREDENTIALS} | jq -r .Credentials.SessionToken)
ACCESS_KEY_ID=$(echo ${CREDENTIALS} | jq -r .Credentials.AccessKeyId)
SECRET_KEY=$(echo ${CREDENTIALS} | jq -r .Credentials.SecretKey)

aws iot attach-policy \
    --policy-name "iot-policy-for-cognito-auth" \
    --target $IDENTITY_ID

iot_data_endpoint=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)
topic=test/iot

for i in $(seq 1 5); do
    curl -w '\n' \
        -H "X-Amz-Security-Token: ${SESSION_TOKEN}" \
        --aws-sigv4 aws:amz:${AWS_REGION}:iotdevicegateway \
        --user ${ACCESS_KEY_ID}:${SECRET_KEY} \
        -X POST \
        https://$iot_data_endpoint/topics/$topic?qos=1 \
        --data "{\"index\": $i}"
done
