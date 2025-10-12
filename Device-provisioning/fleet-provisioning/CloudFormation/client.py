from logging import getLogger, StreamHandler, DEBUG
import os
import uuid
import time
import threading
from awscrt import mqtt
from awsiot import iotidentity
import mqtt_client_wrapper

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

class FleetProvisioningClient:
    def __init__(self, endpoint, cert_path, key_path, ca_path,
                 template_name="FleetProvisioningTemplate", region='us-east-1'):
        self.endpoint = endpoint
        self.region = region
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        self.template_name = template_name
        self.device_id = str(uuid.uuid4())
        self.client_id = f"claiming-device-{self.device_id}"

        # response
        self.create_keys_response = None
        self.register_thing_response = None
        self.is_sample_done = threading.Event()
        self.mqtt_connection = None
        self.identity_client = None

        if ca_path == 'certificate/root-ca.pem':
            self._download_root_ca()

    def _download_root_ca(self):
        import urllib.request
        try:
            urllib.request.urlretrieve(
                'https://www.amazontrust.com/repository/AmazonRootCA1.pem',
                self.ca_path
            )
            logger.debug(f"Successfully downloaded Root CA certificate: {self.ca_path}")
        except Exception as e:
            logger.critical(f"Failed to download Root CA certificate : {e}")

    def _create_keys_accepted(self, response):
        try:
            self.create_keys_response = response
            logger.info("_create_keys_accepted")
            logger.info(f"certificate_id: {response.certificate_id}")
        except Exception as e:
            logger.error(f"CreateKeysAndCertificate: {e}")

    def _create_keys_rejected(self, rejected):
        logger.error(f"_create_keys_rejected: CreateKeysAndCertificate")
        logger.error(f"error_code: {rejected.error_code}")
        logger.error(f"error_message: {rejected.error_message}")
        logger.error(f"status_code: {rejected.status_code}")

    def _register_thing_accepted(self, response):
        try:
            self.register_thing_response = response
            logger.info("_register_thing_accepted")
            logger.info(f"Thing: {response.thing_name}")
        except Exception as e:
            logger.error(f"RegisterThing: {e}")

    def _register_thing_rejected(self, rejected):
        logger.error(f"RegisterThing")
        logger.error(f"error_code: {rejected.error_code}")
        logger.error(f"error_message: {rejected.error_message}")
        logger.error(f"status_code: {rejected.status_code}")

    def provision_device(self):
        logger.info(f"Started provisioning with device ID: {self.device_id}")

        try:
            self.mqtt_connection = mqtt_client_wrapper.get_connection(
                endpoint=self.endpoint,
                cert_filepath=self.cert_path,
                pri_key_filepath=self.key_path,
                ca_filepath=self.ca_path,
                client_id=self.client_id
            )

            self.identity_client = iotidentity.IotIdentityClient(self.mqtt_connection)

            logger.debug("---------------------Subscribe to CreateKeysAndCertificate---------------------")

            create_keys_subscription_request = iotidentity.CreateKeysAndCertificateSubscriptionRequest()

            create_keys_accepted_future, _ = self.identity_client.subscribe_to_create_keys_and_certificate_accepted(
                request=create_keys_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._create_keys_accepted
            )
            create_keys_accepted_future.result()

            create_keys_rejected_future, _ = self.identity_client.subscribe_to_create_keys_and_certificate_rejected(
                request=create_keys_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._create_keys_rejected
            )
            create_keys_rejected_future.result()

            logger.debug("---------------------CreateKeysAndCertificate---------------------")
            publish_future = self.identity_client.publish_create_keys_and_certificate(
                request=iotidentity.CreateKeysAndCertificateRequest(),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            publish_future.result()
            logger.debug("---------------------CreateKeysAndCertificate---------------------")

            self._wait_for_create_keys_response()

            if self.create_keys_response is None:
                raise Exception('Failed CreateKeysAndCertificate API')

            logger.debug("---------------------Subscribe to RegisterThing---------------------")

            register_thing_subscription_request = iotidentity.RegisterThingSubscriptionRequest(
                template_name=self.template_name
            )

            register_thing_accepted_future, _ = self.identity_client.subscribe_to_register_thing_accepted(
                request=register_thing_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._register_thing_accepted
            )
            register_thing_accepted_future.result()

            register_thing_rejected_future, _ = self.identity_client.subscribe_to_register_thing_rejected(
                request=register_thing_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._register_thing_rejected
            )
            register_thing_rejected_future.result()

            logger.debug("---------------------RegisterThing---------------------")
            register_thing_request = iotidentity.RegisterThingRequest(
                template_name=self.template_name,
                certificate_ownership_token=self.create_keys_response.certificate_ownership_token,
                parameters={
                    "DeviceId": self.device_id
                }
            )

            register_thing_future = self.identity_client.publish_register_thing(
                register_thing_request,
                mqtt.QoS.AT_LEAST_ONCE
            )
            register_thing_future.result()
            logger.debug("---------------------RegisterThing---------------------")

            self._wait_for_register_thing_response()

            if self.register_thing_response is None:
                raise Exception('Failed RegisterThing')

            return {
                'certificate': self.create_keys_response,
                'thing': self.register_thing_response
            }

        finally:
            if self.mqtt_connection:
                logger.debug("Will disconnect")
                disconnect_future = self.mqtt_connection.disconnect()
                disconnect_future.result()

    def _wait_for_create_keys_response(self):
        loop_count = 0
        while loop_count < 10 and self.create_keys_response is None:
            if self.create_keys_response is not None:
                break
            logger.debug('Waiting for the response of CreateKeysAndCertificate')
            loop_count += 1
            time.sleep(1)

    def _wait_for_register_thing_response(self):
        loop_count = 0
        while loop_count < 20 and self.register_thing_response is None:
            if self.register_thing_response is not None:
                break
            logger.debug('Waiting for the response of RegisterThing')
            loop_count += 1
            time.sleep(1)

def main():
    endpoint = "xxx.iot.ap-northeast-1.amazonaws.com"
    provisioning_client = FleetProvisioningClient(
        endpoint=endpoint,
        cert_path='certificate/claim-cert.pem',
        key_path='certificate/claim-private.key',
        ca_path='certificate/root-ca.pem',
        template_name='FleetProvisioningTemplate'
    )

    try:
        response = provisioning_client.provision_device()
        logger.info("Succeed Fleet Provisioning !")
        logger.debug(f"Certificate ID: {response['certificate'].certificate_id}")
        logger.debug(f"Thing: {response['thing'].thing_name}")

        if response['certificate'].certificate_pem:
            with open('certificate/device-cert.pem', 'w') as f:
                f.write(response['certificate'].certificate_pem)
            logger.debug("Saved new device certificate to certificate/device-cert.pem")

        if response['certificate'].private_key:
            with open('certificate/device-private.key', 'w') as f:
                f.write(response['certificate'].private_key)
            logger.debug("Saved new private key to certificate/device-private.key")

    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()
