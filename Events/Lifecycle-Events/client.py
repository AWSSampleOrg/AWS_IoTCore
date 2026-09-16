import mqtt3

# -*- encoding:utf-8 -*-
import logging
import os
import time

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
        client_id="Thing1",
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

    logger.debug("Press Ctrl+C to disconnect...")

    return mqtt_connection


if __name__ == "__main__":
    while True:
        mqtt_connection = main()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            disconnect_future = mqtt_connection.disconnect()
            disconnect_future.result()
