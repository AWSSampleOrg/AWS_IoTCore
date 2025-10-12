from logging import getLogger, StreamHandler, DEBUG
import os
import sys
import awscrt
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    logger.debug(f"Connection interrupted. error: {error}")

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    logger.debug(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        logger.debug("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    logger.debug(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")

# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    logger.debug(f"Received message from topic '{topic}': {payload}")

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    logger.debug(f"Connection Successful with return code: {callback_data.return_code} session present: {callback_data.session_present}")

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    logger.debug(f"Connection failed with error code: {callback_data.error}")

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    logger.debug("Connection closed")

def get_connection(
    endpoint: str,
    cert_filepath: str,
    pri_key_filepath: str,
    client_id: str,
    ca_filepath: str
) -> awscrt.mqtt.Connection:
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        client_bootstrap=client_bootstrap,
        ca_filepath=ca_filepath,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=6,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed
    )

    logger.debug("Connecting to %s with client ID '%s'...", endpoint, client_id)
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()

    return mqtt_connection
