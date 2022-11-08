# -*- encoding:utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import os
# Third party
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False


# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = ""
CLIENT_ID = "Thing1"
PATH_TO_CERT = ""
PATH_TO_KEY = ""
PATH_TO_ROOT = ""
TOPIC = "test/iot"

def get_connection():
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(endpoint=ENDPOINT,
                                                            cert_filepath=PATH_TO_CERT,
                                                            pri_key_filepath=PATH_TO_KEY,
                                                            client_bootstrap=client_bootstrap,
                                                            ca_filepath=PATH_TO_ROOT,
                                                            client_id=CLIENT_ID,
                                                            clean_session=False,
                                                            keep_alive_secs=6)

    logger.debug("Connecting to %s with client ID '%s'...", ENDPOINT, CLIENT_ID)
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()

    return mqtt_connection

def main():
    mqtt_connection = get_connection()

    data = "Hello World".encode("UTF-8")
    logger.debug(data)

    mqtt_connection.publish(topic=TOPIC, payload=bytearray(data), qos=mqtt.QoS.AT_LEAST_ONCE)


    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()


if __name__ == "__main__":
    main()
