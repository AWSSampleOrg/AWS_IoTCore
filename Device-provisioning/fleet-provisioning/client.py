from logging import getLogger, StreamHandler, DEBUG
import os
import boto3
import uuid
import mqtt_client_wrapper
import iotidentity_wrapper

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False


def download_root_ca(ca_path: str):
    import urllib.request

    try:
        urllib.request.urlretrieve(
            "https://www.amazontrust.com/repository/AmazonRootCA1.pem", ca_path
        )
        logger.debug(f"Successfully downloaded Root CA certificate: {ca_path}")
    except Exception as e:
        logger.critical(f"Failed to download Root CA certificate : {e}")
        raise e


def provision_device(
    endpoint: str,
    cert_path: str,
    device_id: str,
    key_path: str,
    ca_path: str,
    client_id: str,
    template_name: str,
):
    logger.info(f"Started provisioning with device ID: {device_id}")

    try:
        mqtt_connection = mqtt_client_wrapper.get_connection(
            endpoint=endpoint,
            cert_filepath=cert_path,
            pri_key_filepath=key_path,
            ca_filepath=ca_path,
            client_id=client_id,
        )

        identity_client = iotidentity_wrapper.get_iot_identity_client(mqtt_connection)

        create_keys_response = (
            iotidentity_wrapper.subscribe_to_create_keys_and_certificate_accepted(
                identity_client=identity_client
            )
        )

        register_thing_response = (
            iotidentity_wrapper.register_thing_subscription_request(
                identity_client=identity_client,
                template_name=template_name,
                parameters={"DeviceId": device_id},
                create_keys_response=create_keys_response,
            )
        )

        return {"certificate": create_keys_response, "thing": register_thing_response}

    finally:
        if mqtt_connection:
            logger.debug("Will disconnect")
            disconnect_future = mqtt_connection.disconnect()
            disconnect_future.result()


def main():
    ca_path = "certificate/root-ca.pem"
    download_root_ca(ca_path)
    device_id = str(uuid.uuid4())

    endpoint = boto3.client("iot").describe_endpoint(endpointType="iot:Data-ATS")[
        "endpointAddress"
    ]
    response = provision_device(
        endpoint=endpoint,
        client_id=f"claiming-device-{device_id}",
        device_id=device_id,
        cert_path="certificate/claim-cert.pem",
        key_path="certificate/claim-private.key",
        ca_path=ca_path,
        template_name="FleetProvisioningTemplate",
    )

    try:
        logger.info("Succeed Fleet Provisioning !")
        logger.debug(f"Certificate ID: {response['certificate'].certificate_id}")
        logger.debug(f"Thing: {response['thing'].thing_name}")

        if response["certificate"].certificate_pem:
            with open("certificate/device-cert.pem", "w") as f:
                f.write(response["certificate"].certificate_pem)
            logger.debug("Saved new device certificate to certificate/device-cert.pem")

        if response["certificate"].private_key:
            with open("certificate/device-private.key", "w") as f:
                f.write(response["certificate"].private_key)
            logger.debug("Saved new private key to certificate/device-private.key")

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
