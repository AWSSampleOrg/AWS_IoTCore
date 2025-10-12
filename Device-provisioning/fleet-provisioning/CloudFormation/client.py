import uuid
import time
import threading
from awscrt import mqtt
from awsiot import iotidentity, mqtt_connection_builder
from concurrent.futures import Future

class FleetProvisioningClient:
    def __init__(self, endpoint, cert_path, key_path, ca_path,
                 template_name="MyDeviceTemplate", region='us-east-1'):
        self.endpoint = endpoint
        self.region = region
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        self.template_name = template_name
        self.device_id = str(uuid.uuid4())
        self.client_id = f"claiming-device-{self.device_id}"

        # レスポンス格納用
        self.create_keys_response = None
        self.register_thing_response = None
        self.is_sample_done = threading.Event()
        self.mqtt_connection = None
        self.identity_client = None

        # AWS IoT Core のルートCAをダウンロード（初回のみ）
        if ca_path == 'certificate/root-ca.pem':
            self._download_root_ca()

    def _download_root_ca(self):
        """AWS IoT CoreのルートCA証明書をダウンロード"""
        import urllib.request
        try:
            urllib.request.urlretrieve(
                'https://www.amazontrust.com/repository/AmazonRootCA1.pem',
                self.ca_path
            )
            print(f"ルートCA証明書をダウンロードしました: {self.ca_path}")
        except Exception as e:
            print(f"ルートCA証明書のダウンロードに失敗しました: {e}")

    def _on_connection_interrupted(self, connection, error, **kwargs):
        print(f"接続が中断されました。エラー: {error}")

    def _on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        print(f"接続が復旧しました。return_code: {return_code} session_present: {session_present}")

    def _on_disconnected(self, disconnect_future):
        print("切断されました。")
        self.is_sample_done.set()

    def _create_keys_accepted(self, response):
        """CreateKeysAndCertificate成功時のコールバック"""
        try:
            self.create_keys_response = response
            print("新しい証明書とキーが正常に作成されました！")
            print(f"証明書ID: {response.certificate_id}")
        except Exception as e:
            print(f"CreateKeysAndCertificate応答処理エラー: {e}")

    def _create_keys_rejected(self, rejected):
        """CreateKeysAndCertificate拒否時のコールバック"""
        print(f"CreateKeysAndCertificate要求が拒否されました。")
        print(f"エラーコード: {rejected.error_code}")
        print(f"エラーメッセージ: {rejected.error_message}")
        print(f"ステータスコード: {rejected.status_code}")

    def _register_thing_accepted(self, response):
        """RegisterThing成功時のコールバック"""
        try:
            self.register_thing_response = response
            print("デバイス登録が正常に完了しました！")
            print(f"Thing名: {response.thing_name}")
        except Exception as e:
            print(f"RegisterThing応答処理エラー: {e}")

    def _register_thing_rejected(self, rejected):
        """RegisterThing拒否時のコールバック"""
        print(f"RegisterThing要求が拒否されました。")
        print(f"エラーコード: {rejected.error_code}")
        print(f"エラーメッセージ: {rejected.error_message}")
        print(f"ステータスコード: {rejected.status_code}")

    def provision_device(self):
        print(f"デバイス ID: {self.device_id} でプロビジョニングを開始します")

        try:
            # MQTT接続を作成
            print("MQTT接続を作成中...")
            self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=self.endpoint,
                port=8883,
                cert_filepath=self.cert_path,
                pri_key_filepath=self.key_path,
                ca_filepath=self.ca_path,
                on_connection_interrupted=self._on_connection_interrupted,
                on_connection_resumed=self._on_connection_resumed,
                client_id=self.client_id,
                clean_session=False,
                keep_alive_secs=30
            )

            print(f"エンドポイント {self.endpoint} にクライアントID '{self.client_id}' で接続中...")
            connected_future = self.mqtt_connection.connect()

            self.identity_client = iotidentity.IotIdentityClient(self.mqtt_connection)
            connected_future.result()
            print("接続成功！")

            # 第1段階: CreateKeysAndCertificate のサブスクリプション
            print("CreateKeysAndCertificate トピックにサブスクライブ中...")

            create_keys_subscription_request = iotidentity.CreateKeysAndCertificateSubscriptionRequest()

            # Accepted サブスクリプション
            create_keys_accepted_future, _ = self.identity_client.subscribe_to_create_keys_and_certificate_accepted(
                request=create_keys_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._create_keys_accepted
            )
            create_keys_accepted_future.result()

            # Rejected サブスクリプション
            create_keys_rejected_future, _ = self.identity_client.subscribe_to_create_keys_and_certificate_rejected(
                request=create_keys_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._create_keys_rejected
            )
            create_keys_rejected_future.result()

            # CreateKeysAndCertificate 要求を発行
            print("CreateKeysAndCertificate 要求を送信中...")
            publish_future = self.identity_client.publish_create_keys_and_certificate(
                request=iotidentity.CreateKeysAndCertificateRequest(),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            publish_future.result()
            print("CreateKeysAndCertificate 要求を送信しました")

            # 応答を待機
            self._wait_for_create_keys_response()

            if self.create_keys_response is None:
                raise Exception('CreateKeysAndCertificate APIが成功しませんでした')

            # 第2段階: RegisterThing のサブスクリプション
            print("RegisterThing トピックにサブスクライブ中...")

            register_thing_subscription_request = iotidentity.RegisterThingSubscriptionRequest(
                template_name=self.template_name
            )

            # Accepted サブスクリプション
            register_thing_accepted_future, _ = self.identity_client.subscribe_to_register_thing_accepted(
                request=register_thing_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._register_thing_accepted
            )
            register_thing_accepted_future.result()

            # Rejected サブスクリプション
            register_thing_rejected_future, _ = self.identity_client.subscribe_to_register_thing_rejected(
                request=register_thing_subscription_request,
                qos=mqtt.QoS.AT_LEAST_ONCE,
                callback=self._register_thing_rejected
            )
            register_thing_rejected_future.result()

            # RegisterThing 要求を作成・送信
            print("RegisterThing 要求を送信中...")
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
            print("RegisterThing 要求を送信しました")

            # 応答を待機
            self._wait_for_register_thing_response()

            if self.register_thing_response is None:
                raise Exception('RegisterThing APIが成功しませんでした')

            return {
                'certificate': self.create_keys_response,
                'thing': self.register_thing_response
            }

        finally:
            if self.mqtt_connection:
                print("接続を切断中...")
                disconnect_future = self.mqtt_connection.disconnect()
                disconnect_future.add_done_callback(self._on_disconnected)
                self.is_sample_done.wait()

    def _wait_for_create_keys_response(self):
        """CreateKeysAndCertificate応答を待機"""
        loop_count = 0
        while loop_count < 10 and self.create_keys_response is None:
            if self.create_keys_response is not None:
                break
            print('CreateKeysAndCertificate応答を待機中...')
            loop_count += 1
            time.sleep(1)

    def _wait_for_register_thing_response(self):
        """RegisterThing応答を待機"""
        loop_count = 0
        while loop_count < 20 and self.register_thing_response is None:
            if self.register_thing_response is not None:
                break
            print('RegisterThing応答を待機中...')
            loop_count += 1
            time.sleep(1)

def main():
    # エンドポイントを指定
    endpoint = "xxx.iot.ap-northeast-1.amazonaws.com"

    print(f"AWS IoT Core エンドポイント: {endpoint}")

    # クレーム証明書を使用してFleet Provisioningクライアントを作成
    provisioning_client = FleetProvisioningClient(
        endpoint=endpoint,
        cert_path='certificate/claim-cert.pem',
        key_path='certificate/claim-private.key',
        ca_path='certificate/root-ca.pem',
        template_name='MyDeviceTemplate'
    )

    try:
        response = provisioning_client.provision_device()
        print("\nFleet Provisioning が正常に完了しました！")
        print(f"新しい証明書ID: {response['certificate'].certificate_id}")
        print(f"Thing名: {response['thing'].thing_name}")

        # 新しい証明書とキーを保存
        if response['certificate'].certificate_pem:
            with open('device-cert.pem', 'w') as f:
                f.write(response['certificate'].certificate_pem)
            print("新しいデバイス証明書を device-cert.pem に保存しました")

        if response['certificate'].private_key:
            with open('device-private.key', 'w') as f:
                f.write(response['certificate'].private_key)
            print("新しいプライベートキーを device-private.key に保存しました")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
