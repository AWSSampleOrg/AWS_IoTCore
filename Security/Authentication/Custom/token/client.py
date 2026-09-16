# -*- encoding:utf-8 -*-
import logging
import os
import json
import time

import boto3
import awscrt

import mqtt3

# logger setting
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", logging.DEBUG))
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)s] %(funcName)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
)
logger.addHandler(handler)
logger.propagate = False

iot_client = boto3.client("iot")
ENDPOINT = iot_client.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]

authorizer_description = iot_client.describe_authorizer(
    authorizerName="with-token-authorizer"
)["authorizerDescription"]


def main():
    TOKEN_VALUE = "my-test-token"
    SIGNATURE = "echo -n $TOKEN_VALUE | openssl dgst -sha256 -sign id_rsa.key | base64 | tr -d '\n'"
    mqtt_connection = mqtt3.direct_with_custom_authorizer(
        client_id="Thing1",
        ca_filepath=os.path.join(
            os.path.dirname(__file__), "certificates/AmazonRootCA1.pem"
        ),
        # auth_username="auth_username",
        auth_authorizer_name=authorizer_description["authorizerName"],
        # https://docs.aws.amazon.com/iot/latest/developerguide/custom-auth.html#custom-auth-token-signature
        auth_authorizer_signature=SIGNATURE,
        # auth_password="auth_password",
        auth_token_key_name=authorizer_description["tokenKeyName"],
        auth_token_value=TOKEN_VALUE,
    )

    topic = "test/iot"
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic,
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        callback=mqtt3.on_message_received,
    )
    subscribe_result = subscribe_future.result()
    logger.debug(
        f"Subscribed {str(subscribe_result['topic'])} with qos: {str(subscribe_result['qos'])}, packet_id: {packet_id}"
    )

    data = json.dumps({"index": 0})
    logger.debug(data)
    mqtt_connection.publish(
        topic=topic, payload=data, qos=awscrt.mqtt.QoS.AT_LEAST_ONCE
    )
    time.sleep(1)

    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()


if __name__ == "__main__":
    main()
