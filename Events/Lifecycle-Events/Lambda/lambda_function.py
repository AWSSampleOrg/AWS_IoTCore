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


def handle_connected_event(event):
    pass


def handle_disconnected_event(event):
    pass


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    for record in event["Records"]:
        logger.debug(record["body"])
        body = json.loads(record["body"])

        event_type = body["eventType"]
        if event_type == "connected":
            handle_connected_event(body)
        elif event_type == "disconnected":
            handle_disconnected_event(body)
