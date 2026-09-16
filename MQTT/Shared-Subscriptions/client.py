import mqtt3

# -*- encoding:utf-8 -*-
import logging
import os
import sys
import time

import awscrt

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


def main(client_id: str):
    mqtt_connection = mqtt3.mtls_from_path(
        client_id=client_id,
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
        clean_session=True,
    )

    share_name = "consumer"
    topic = "shared-subscriptions/work"

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=f"$share/{share_name}/{topic}",
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        callback=mqtt3.on_message_received,
    )
    subscribe_result = subscribe_future.result()
    logger.debug(
        f"Subscribed {str(subscribe_result['topic'])} with qos: {str(subscribe_result['qos'])}, packet_id: {packet_id}"
    )

    logger.debug("Press Ctrl+C to disconnect...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) >= 2:
        main(argv[1])
