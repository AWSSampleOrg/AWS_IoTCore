# Overview

- AWS IoT Core / Security / Authentication / Client authentication / Amazon Cognito identities
  https://docs.aws.amazon.com/iot/latest/developerguide/cognito-identities.html

- Amplify Gen2 / PubSub
  https://docs.amplify.aws/react/build-a-backend/add-aws-services/pubsub/set-up-pubsub/

## Frontend using Amplify

### Install Libraries

```sh
npm install
```

### Create AWS Resources

```sh
./ampx sandbox
```

### Set Up .env

1. Get IoT Data Endpoint

```sh
iot_data_endpoint=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)
```

2. Create .env file

**Note**

- https://docs.amplify.aws/react/build-a-backend/add-aws-services/pubsub/set-up-pubsub/
  //=====
  PubSub is available with AWS IoT and Generic MQTT Over WebSocket Providers.
  =====//

```
VITE_AWS_REGION=<Your AWS Region>
VITE_IOT_ATS_ENDPOINT=wss://<Your Device Data Endpoint>/mqtt
```

## AWS CLI

Write some essential details shown below

```sh
USER_POOL_ID=
CLIENT_ID=
IDENTITY_POOL_ID=
USER_NAME=
PASSWORD=
```

```sh
./cli.sh
```
