import json
import os
import time
import mqtt3
import awscrt


def main() -> None:
    # Configuration
    mqtt3.CLIENT_ID = "device001"
    mqtt3.PATH_TO_CERT = os.path.join(
        os.path.dirname(__file__),
        "certificates/device_cert_filename.pem",
    )
    mqtt3.PATH_TO_KEY = os.path.join(
        os.path.dirname(__file__),
        "certificates/device_cert_key_filename.key",
    )
    mqtt3.PATH_TO_ROOT = os.path.join(
        os.path.dirname(__file__), "certificates/AmazonRootCA1.pem"
    )

    conn = mqtt3.get_connection()
    topic = f"device/{mqtt3.CLIENT_ID}/data"

    conn.subscribe(
        topic=topic,
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        callback=mqtt3.on_message_received,
    )

    count = 0
    while True:
        conn.publish(
            topic=topic,
            payload=json.dumps({"count": count}),
            qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        )
        count += 1
        time.sleep(5)


if __name__ == "__main__":
    main()
