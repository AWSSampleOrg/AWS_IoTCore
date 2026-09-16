import json
import os
import sys
import time
import awscrt
import mqtt3

certificate_ownership_token: str = ""
certificate_id: str = ""
certificate_pem: str = ""
private_key: str = ""


def on_cert_created(
    topic: str, payload: bytes, dup: bool, qos: awscrt.mqtt.QoS, retain: bool, **kwargs
) -> None:
    mqtt3.on_message_received(topic, payload, dup, qos, retain, **kwargs)

    global certificate_ownership_token, certificate_id, certificate_pem, private_key
    body = json.loads(payload.decode())
    certificate_ownership_token = body["certificateOwnershipToken"]
    certificate_id = body["certificateId"]
    certificate_pem = body["certificatePem"]
    private_key = body["privateKey"]

    this_directory = os.path.dirname(__file__)

    with open(
        os.path.join(
            this_directory,
            "certificates/private_key.pem",
        ),
        "w",
    ) as fp:
        fp.write(private_key)

    with open(
        os.path.join(
            this_directory,
            "certificates/certificate_pem.pem",
        ),
        "w",
    ) as fp:
        fp.write(certificate_pem)

    print(f"Certificate created {certificate_id}")


def main(device_serial_number) -> None:
    mqtt_connection = mqtt3.get_connection(
        client_id=device_serial_number,
        cert_filepath="certificates/claim.cert.pem",
        pri_key_filepath="certificates/claim.private.key",
        ca_filepath="certificates/AmazonRootCA1.pem",
    )

    subscribe_accepted_future, _ = mqtt_connection.subscribe(
        topic="$aws/certificates/create/json/accepted",
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        callback=on_cert_created,
    )
    subscribe_rejected_future, _ = mqtt_connection.subscribe(
        topic="$aws/certificates/create/json/rejected",
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        callback=mqtt3.on_message_received,
    )
    subscribe_accepted_future.result()
    subscribe_rejected_future.result()

    mqtt_connection.publish(
        topic="$aws/certificates/create/json",
        payload=json.dumps({}),
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
    )

    time.sleep(2)

    template_name = "fleet-provisioning-template"
    for topic in [
        f"$aws/provisioning-templates/{template_name}/provision/json/accepted",
        f"$aws/provisioning-templates/{template_name}/provision/json/rejected",
    ]:
        subscribe_future, _ = mqtt_connection.subscribe(
            topic=topic,
            qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
            callback=mqtt3.on_message_received,
        )
        subscribe_future.result()

    mqtt_connection.publish(
        topic=f"$aws/provisioning-templates/{template_name}/provision/json",
        payload=json.dumps(
            {
                "certificateOwnershipToken": certificate_ownership_token,
                "parameters": {"SerialNumber": device_serial_number},
            }
        ),
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
    )

    time.sleep(2)
    print("Provisioning complete")


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print("python client.py <certificates/claim.cert.pem serial number>")
    else:
        main(argv[1])
