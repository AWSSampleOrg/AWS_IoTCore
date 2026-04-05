import time
from awsiot import iotidentity
from awscrt import mqtt
import mqtt3

cert_ownership_token: str = ""
cert_id: str = ""
cert_pem: str = ""
private_key: str = ""


def on_cert_created(response: iotidentity.CreateKeysAndCertificateResponse) -> None:
    global cert_ownership_token, cert_id, cert_pem, private_key
    cert_ownership_token = response.certificate_ownership_token
    cert_id = response.certificate_id
    cert_pem = response.certificate_pem
    private_key = response.private_key
    print("Certificate created")


def on_thing_registered(response: iotidentity.RegisterThingResponse) -> None:
    print(f"Thing registered: {response.thing_name}")


def main() -> None:
    # Configuration
    mqtt3.CLIENT_ID = "claim-device"
    mqtt3.PATH_TO_CERT = "certificates/claim.cert.pem"
    mqtt3.PATH_TO_KEY = "certificates/claim.private.key"
    mqtt3.PATH_TO_ROOT = "certificates/AmazonRootCA1.pem"

    TEMPLATE_NAME = "fleet-template"
    SERIAL_NUMBER = "123456789"

    conn = mqtt3.get_connection()
    identity = iotidentity.IotIdentityClient(conn)

    # Request permanent certificate
    identity.subscribe_to_create_keys_and_certificate_accepted(
        request=iotidentity.CreateKeysAndCertificateSubscriptionRequest(),
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_cert_created,
    )

    identity.publish_create_keys_and_certificate(
        request=iotidentity.CreateKeysAndCertificateRequest(),
        qos=mqtt.QoS.AT_LEAST_ONCE,
    )

    time.sleep(2)

    # Register thing
    identity.subscribe_to_register_thing_accepted(
        request=iotidentity.RegisterThingSubscriptionRequest(
            templateName=TEMPLATE_NAME
        ),
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_thing_registered,
    )

    identity.publish_register_thing(
        request=iotidentity.RegisterThingRequest(
            templateName=TEMPLATE_NAME,
            certificateOwnershipToken=cert_ownership_token,
            parameters={"SerialNumber": SERIAL_NUMBER},
        ),
        qos=mqtt.QoS.AT_LEAST_ONCE,
    )

    time.sleep(2)
    print("Provisioning complete")


if __name__ == "__main__":
    main()
