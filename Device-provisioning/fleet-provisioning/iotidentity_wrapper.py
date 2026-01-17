from logging import getLogger, StreamHandler, DEBUG
import os
import time
import awscrt
from awscrt import mqtt
from awsiot import iotidentity

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False


def register_thing_subscription_request(
    identity_client: iotidentity.IotIdentityClient,
    template_name: str,
    parameters: dict,
    create_keys_response,
):
    register_thing_response = None

    def _register_thing_accepted(response):
        try:
            nonlocal register_thing_response
            register_thing_response = response
            logger.info("_register_thing_accepted")
            logger.info(f"Thing: {response.thing_name}")
        except Exception as e:
            logger.error(f"RegisterThing: {e}")

    def _register_thing_rejected(rejected):
        logger.error(f"RegisterThing")
        logger.error(f"error_code: {rejected.error_code}")
        logger.error(f"error_message: {rejected.error_message}")
        logger.error(f"status_code: {rejected.status_code}")

    logger.debug("---------------------Subscribe to RegisterThing---------------------")

    register_thing_subscription_request = iotidentity.RegisterThingSubscriptionRequest(
        template_name=template_name
    )

    register_thing_accepted_future, _ = (
        identity_client.subscribe_to_register_thing_accepted(
            request=register_thing_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=_register_thing_accepted,
        )
    )
    register_thing_accepted_future.result()

    register_thing_rejected_future, _ = (
        identity_client.subscribe_to_register_thing_rejected(
            request=register_thing_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=_register_thing_rejected,
        )
    )
    register_thing_rejected_future.result()

    # Publish RegisterThing request
    logger.debug("---------------------RegisterThing---------------------")
    register_thing_request = iotidentity.RegisterThingRequest(
        template_name=template_name,
        certificate_ownership_token=create_keys_response.certificate_ownership_token,
        parameters=parameters,
    )

    register_thing_future = identity_client.publish_register_thing(
        register_thing_request, mqtt.QoS.AT_LEAST_ONCE
    )
    register_thing_future.result()
    logger.debug("---------------------RegisterThing---------------------")

    # Wait for response
    loop_count = 0
    while loop_count < 20 and register_thing_response is None:
        logger.debug("Waiting for the response of RegisterThing")
        loop_count += 1
        time.sleep(1)

    if register_thing_response is None:
        raise Exception("Failed RegisterThing")

    return register_thing_response


def subscribe_to_create_keys_and_certificate_accepted(
    identity_client: iotidentity.IotIdentityClient,
):
    create_keys_response = None

    def _create_keys_accepted(response):
        try:
            nonlocal create_keys_response
            create_keys_response = response
            logger.info("_create_keys_accepted")
            logger.info(f"certificate_id: {response.certificate_id}")
        except Exception as e:
            logger.error(f"CreateKeysAndCertificate: {e}")

    def _create_keys_rejected(rejected):
        logger.error(f"_create_keys_rejected: CreateKeysAndCertificate")
        logger.error(f"error_code: {rejected.error_code}")
        logger.error(f"error_message: {rejected.error_message}")
        logger.error(f"status_code: {rejected.status_code}")

    logger.debug(
        "---------------------Subscribe to CreateKeysAndCertificate---------------------"
    )

    create_keys_subscription_request = (
        iotidentity.CreateKeysAndCertificateSubscriptionRequest()
    )

    create_keys_accepted_future, _ = (
        identity_client.subscribe_to_create_keys_and_certificate_accepted(
            request=create_keys_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=_create_keys_accepted,
        )
    )
    create_keys_accepted_future.result()

    create_keys_rejected_future, _ = (
        identity_client.subscribe_to_create_keys_and_certificate_rejected(
            request=create_keys_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=_create_keys_rejected,
        )
    )
    create_keys_rejected_future.result()

    # Publish the request
    logger.debug("---------------------CreateKeysAndCertificate---------------------")
    publish_future = identity_client.publish_create_keys_and_certificate(
        request=iotidentity.CreateKeysAndCertificateRequest(),
        qos=mqtt.QoS.AT_LEAST_ONCE,
    )
    publish_future.result()
    logger.debug("---------------------CreateKeysAndCertificate---------------------")

    # Wait for response
    loop_count = 0
    while loop_count < 10 and create_keys_response is None:
        logger.debug("Waiting for the response of CreateKeysAndCertificate")
        loop_count += 1
        time.sleep(1)

    if create_keys_response is None:
        raise Exception("Failed CreateKeysAndCertificate API")

    return create_keys_response


def get_iot_identity_client(
    mqtt_connection: awscrt.mqtt.Connection,
) -> iotidentity.IotIdentityClient:
    return iotidentity.IotIdentityClient(mqtt_connection)
