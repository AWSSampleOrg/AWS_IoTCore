# -*- encoding:utf-8 -*-
import logging
import os
import json
import time
import threading
from awsiot import mqtt5_client_builder

from awscrt import mqtt5
import boto3

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

# --------------------------------- ARGUMENT PARSING END -----------------------------------------
TIMEOUT = 100
# Events used within callbacks to progress sample
connection_success_event = threading.Event()
stopped_event = threading.Event()
received_all_event = threading.Event()


# Callback when any publish is received
def on_publish_received(publish_packet_data: mqtt5.PublishReceivedData):
    publish_packet = publish_packet_data.publish_packet
    logger.debug(
        "==== Received message from topic '{}': {} ====\n".format(
            publish_packet.topic, publish_packet.payload.decode("utf-8")
        )
    )


# Callback for the lifecycle event Stopped
def on_lifecycle_stopped(lifecycle_stopped_data: mqtt5.LifecycleStoppedData):
    logger.debug("Lifecycle Stopped\n")
    stopped_event.set()


# Callback for lifecycle event Attempting Connect
def on_lifecycle_attempting_connect(
    lifecycle_attempting_connect_data: mqtt5.LifecycleAttemptingConnectData,
):
    logger.debug(lifecycle_attempting_connect_data)


# Callback for the lifecycle event Connection Success
def on_lifecycle_connection_success(
    lifecycle_connect_success_data: mqtt5.LifecycleConnectSuccessData,
):
    connack_packet = lifecycle_connect_success_data.connack_packet
    logger.debug(
        "Lifecycle Connection Success with reason code:{}\n".format(
            repr(connack_packet.reason_code)
        )
    )
    logger.debug("Session Present: {}\n".format(connack_packet.session_present))
    logger.debug(connack_packet)
    connection_success_event.set()


# Callback for the lifecycle event Connection Failure
def on_lifecycle_connection_failure(
    lifecycle_connection_failure: mqtt5.LifecycleConnectFailureData,
):
    logger.debug(
        "Lifecycle Connection Failure with exception:{}".format(
            lifecycle_connection_failure.exception
        )
    )


# Callback for the lifecycle event Disconnection
def on_lifecycle_disconnection(
    lifecycle_disconnect_data: mqtt5.LifecycleDisconnectData,
):
    logger.debug(
        "Lifecycle Disconnected with reason code:{}".format(
            lifecycle_disconnect_data.disconnect_packet.reason_code
            if lifecycle_disconnect_data.disconnect_packet
            else "None"
        )
    )


def get_connection(
    cert_filePath=os.path.join(
        os.path.dirname(__file__),
        "certificates/device_cert_filename.pem",
    ),
    pri_key_filepath=os.path.join(
        os.path.dirname(__file__),
        "certificates/device_cert_key_filename.key",
    ),
):
    mqtt_connection = mqtt5_client_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=cert_filePath,
        pri_key_filepath=pri_key_filepath,
        on_publish_received=on_publish_received,
        on_lifecycle_stopped=on_lifecycle_stopped,
        on_lifecycle_attempting_connect=on_lifecycle_attempting_connect,
        on_lifecycle_connection_success=on_lifecycle_connection_success,
        on_lifecycle_connection_failure=on_lifecycle_connection_failure,
        on_lifecycle_disconnection=on_lifecycle_disconnection,
        # Persistent session
        # https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html#mqtt-persistent-sessions
        # session_behavior=mqtt5.ClientSessionBehaviorType.REJOIN_ALWAYS,
        # connect_options=mqtt5.ConnectPacket(
        #     client_id=CLIENT_ID, session_expiry_interval_sec=3600
        # ),
    )
    mqtt_connection.start()
    if not connection_success_event.wait(TIMEOUT):
        raise TimeoutError("Connection timeout")

    return mqtt_connection


def main():
    mqtt_connection = get_connection()

    topic = "test/iot"

    subscribe_future = mqtt_connection.subscribe(
        subscribe_packet=mqtt5.SubscribePacket(
            subscriptions=[
                mqtt5.Subscription(topic_filter=topic, qos=mqtt5.QoS.AT_LEAST_ONCE)
            ]
        )
    )
    suback = subscribe_future.result(TIMEOUT)
    logger.debug(
        f"Subscribed: {suback.reason_string}, user_properties: {suback.user_properties}, reason_codes: {suback.reason_codes}"
    )

    data = json.dumps({"index": 0})
    logger.debug(data)
    mqtt_connection.publish(
        publish_packet=mqtt5.PublishPacket(
            topic=topic, payload=data, qos=mqtt5.QoS.AT_LEAST_ONCE
        )
    )
    time.sleep(1)

    mqtt_connection.stop()
    stopped_event.wait(TIMEOUT)


if __name__ == "__main__":
    main()
