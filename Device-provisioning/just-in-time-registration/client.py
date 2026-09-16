import json
import os
import sys
import time
import mqtt3
import awscrt


def get_mqtt_connection(device_serial_number: str):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return mqtt3.get_connection(
                client_id=device_serial_number,
                cert_filepath=os.path.join(
                    os.path.dirname(__file__),
                    "certificates/ca_and_device_certificate.pem",
                ),
                pri_key_filepath=os.path.join(
                    os.path.dirname(__file__),
                    "certificates/device_cert_key_filename.key",
                ),
                ca_filepath=os.path.join(
                    os.path.dirname(__file__), "certificates/AmazonRootCA1.pem"
                ),
            )
        except Exception as e:
            print(f"Connection failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise e


def main(device_serial_number) -> None:
    conn = get_mqtt_connection(device_serial_number)
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
    argv = sys.argv
    if len(argv) != 2:
        print("python client.py <certificates/device_cert_filename.pem serial number>")
    else:
        main(argv[1])
