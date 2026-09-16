import mqtt3

# -*- encoding:utf-8 -*-
import logging
import os
import json
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


def main():
    mqtt_connection = mqtt3.mtls_from_path(
        client_id="publisher",
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
    )

    data = json.dumps({"state": {"desired": {"percentage": 0.8}}})
    logger.debug(data)
    thing_name = "Thing1"
    shadow_name = "shadow"

    mqtt_connection.publish(
        topic=f"$aws/things/{thing_name}/shadow/name/{shadow_name}/update",
        payload=data,
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
    )

    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()


if __name__ == "__main__":
    main()
