# -*- encoding:utf-8 -*-
import base64
import json
from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL
import os
import sys
# Third party
import boto3

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LogLevel", DEBUG))
logger.addHandler(handler)
logger.propagate = False

# IoT Core
iot_core = boto3.client('iot-data')


def lambda_handler(event,context):
    logger.info(json.dumps(event))

    return {
        "statusCode" : 200,
        "body" : json.dumps({"message" : "OK"})
    }
