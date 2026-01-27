import json
import base64
import os

REGION = os.environ["AWS_DEFAULT_REGION"]

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "iot:Connect",
            "Resource": f"arn:aws:iot:{REGION}:*:client/*",
        },
        {
            "Effect": "Allow",
            "Action": [
                "iot:Publish",
                "iot:Receive",
            ],
            "Resource": f"arn:aws:iot:{REGION}:*:topic/*",
        },
        {
            "Effect": "Allow",
            "Action": "iot:Subscribe",
            "Resource": f"arn:aws:iot:{REGION}:*:topicfilter/*",
        },
    ],
}


def lambda_handler(event, context):
    print(json.dumps(event))

    is_authenticated = False
    username = ""
    password = ""

    if "protocolData" in event:
        protocolData = event["protocolData"]
        if "mqtt" in protocolData:
            mqtt = protocolData["mqtt"]
            if "username" in mqtt:
                username = mqtt["username"].split("?")[0]
            if "password" in mqtt:
                password = base64.b64decode(mqtt["password"]).decode()

            print("username: {}, password: {}".format(username, password))
            if username == "auth_username" and password == "auth_password":
                is_authenticated = True

    print("isAuthenticated: {}".format(is_authenticated))

    principal_id = "CustomAuthId"
    disconnect = 84000
    refresh = 300

    return {
        "isAuthenticated": is_authenticated,
        "principalId": principal_id,
        "disconnectAfterInSeconds": disconnect,
        "refreshAfterInSeconds": refresh,
        "policyDocuments": [policy],
    }
