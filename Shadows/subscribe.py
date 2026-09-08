import mqtt3

# -*- encoding:utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import os
import json
import time

import awscrt

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False


def main():
    mqtt_connection = mqtt3.get_connection(
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

    thing_name = "Thing1"
    shadow_name = "shadow"

    for topic in [
        # f"$aws/things/{thing_name}/shadow/name/{shadow_name}/get",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/get/accepted",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/get/rejected",
        # f"$aws/things/{thing_name}/shadow/name/{shadow_name}/update",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/update/delta",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/update/accepted",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/update/documents",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/update/rejected",
        # f"$aws/things/{thing_name}/shadow/name/{shadow_name}/delete",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/delete/accepted",
        f"$aws/things/{thing_name}/shadow/name/{shadow_name}/delete/rejected",
    ]:
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=topic,
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
    main()
