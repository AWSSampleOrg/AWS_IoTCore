# -*- encoding:utf-8 -*-
import logging
import os
import json
import sys
import time

import awscrt
from awscrt.exceptions import AwsCrtError
from awsiot import mqtt_connection_builder
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

# Define ENDPOINT, MESSAGE and RANGE
iot_client = boto3.client("iot")
ENDPOINT = iot_client.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]


# Callback when connection is accidentally lost.
def on_connection_interrupted(
    connection: awscrt.mqtt.Connection, error: AwsCrtError, **kwargs
):
    logger.debug(f"code={error.code} name={error.name} message={error.message}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(
    connection: awscrt.mqtt.Connection,
    return_code: awscrt.mqtt.ConnectReturnCode,
    session_present: bool,
    **kwargs,
):
    logger.debug(f"return_code: {return_code} session_present: {session_present}")

    if return_code == awscrt.mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        logger.debug("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    logger.debug(f"on_resubscribe_complete: {resubscribe_results}")

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


# Callback when the subscribed topic receives a message
def on_message_received(
    topic: str, payload: bytes, dup: bool, qos: awscrt.mqtt.QoS, retain: bool, **kwargs
):
    logger.debug(
        {
            "topic": topic,
            "dup": dup,
            "qos": qos.value,
            "retain": retain,
        }
    )
    decoded_payload = payload.decode()
    try:
        json_decoded = json.loads(decoded_payload)
        logger.debug(json.dumps(json_decoded, indent=4))
    except Exception:
        logger.debug(decoded_payload)


# Callback when the connection successfully connects
def on_connection_success(connection: awscrt.mqtt.Connection, callback_data):
    assert isinstance(callback_data, awscrt.mqtt.OnConnectionSuccessData)
    logger.debug(
        f"{callback_data.return_code} session present: {callback_data.session_present}"
    )


# Callback when a connection attempt fails
def on_connection_failure(connection: awscrt.mqtt.Connection, callback_data):
    assert isinstance(callback_data, awscrt.mqtt.OnConnectionFailureData)
    logger.debug(callback_data.error)


# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(
    connection: awscrt.mqtt.Connection,
    callback_data: awscrt.mqtt.OnConnectionClosedData,
):
    assert isinstance(callback_data, awscrt.mqtt.OnConnectionFailureData)
    logger.debug(callback_data.error)


def mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=os.path.join(
        os.path.dirname(__file__),
        "certificates/device_cert_filename.pem",
    ),
    pri_key_filepath=os.path.join(
        os.path.dirname(__file__),
        "certificates/device_cert_key_filename.key",
    ),
    ca_filepath=os.path.join(
        os.path.dirname(__file__), "certificates/AmazonRootCA1.pem"
    ),
    client_id="Thing1",
):
    # Spin up resources
    event_loop_group = awscrt.io.EventLoopGroup(1)
    host_resolver = awscrt.io.DefaultHostResolver(event_loop_group)
    client_bootstrap = awscrt.io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        client_bootstrap=client_bootstrap,
        ca_filepath=ca_filepath,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        # Persistent session
        # https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html#mqtt-persistent-sessions
        clean_session=False,
        keep_alive_secs=6,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed,
    )

    logger.debug("Connecting to %s with client ID '%s'...", endpoint, client_id)
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()

    return mqtt_connection


def direct_with_custom_authorizer(
    endpoint=ENDPOINT,
    ca_filepath=os.path.join(
        os.path.dirname(__file__), "certificates/AmazonRootCA1.pem"
    ),
    client_id="Thing1",
    auth_username=None,
    auth_authorizer_name=None,
    auth_authorizer_signature=None,
    auth_password=None,
    auth_token_key_name=None,
    auth_token_value=None,
):
    # Spin up resources
    event_loop_group = awscrt.io.EventLoopGroup(1)
    host_resolver = awscrt.io.DefaultHostResolver(event_loop_group)
    client_bootstrap = awscrt.io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.direct_with_custom_authorizer(
        # Auth
        auth_username=auth_username,
        auth_authorizer_name=auth_authorizer_name,
        auth_authorizer_signature=auth_authorizer_signature,
        auth_password=auth_password,
        auth_token_key_name=auth_token_key_name,
        auth_token_value=auth_token_value,
        # Others
        endpoint=endpoint,
        client_bootstrap=client_bootstrap,
        ca_filepath=ca_filepath,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        # Persistent session
        # https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html#mqtt-persistent-sessions
        clean_session=False,
        keep_alive_secs=6,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed,
    )

    logger.debug("Connecting to %s with client ID '%s'...", endpoint, client_id)
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()

    return mqtt_connection


def main():
    mqtt_connection = mtls_from_path()

    topic = "test/iot"

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic, qos=awscrt.mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
    )
    subscribe_result = subscribe_future.result()
    logger.debug(
        f"Subscribed {str(subscribe_result['topic'])} with qos: {str(subscribe_result['qos'])}, packet_id: {packet_id}"
    )

    data = json.dumps({"index": 0})
    mqtt_connection.publish(
        topic=topic, payload=data, qos=awscrt.mqtt.QoS.AT_LEAST_ONCE
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()


if __name__ == "__main__":
    main()
