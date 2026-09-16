# -*- encoding:utf-8 -*-
import json
from logging import getLogger, StreamHandler, DEBUG
import os
import boto3

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

# IoT Core
iot_core = boto3.client("iot-data")


def lambda_handler(event, context):
    logger.info(event)

    topic = event.get("topic", "unknown")

    response_payload = {
        "message": "Response from Lambda",
        "original_topic": topic,
        "processed": True,
    }

    response_topic = "test/iot/lambda-response"
    iot_core.publish(topic=response_topic, qos=1, payload=json.dumps(response_payload))

    logger.info(f"Published response to {response_topic}")
