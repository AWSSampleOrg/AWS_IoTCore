https://docs.aws.amazon.com/iot/latest/developerguide/diagnosing-connectivity-issues.html

- domain and port
- Protocol. MQTT over TLS, MQTT over WebSocket or HTTPS
- Authentication Type. X509, SigV4 or Cognito
- Timestamp of the devices not connecting
- Frequency. All of a sudden, only few times in the past, or consistently.
- Timestamp of the issue occurred.

# Domain

Check your domain name

```sh
aws iot describe-endpoint --endpoint-type iot:Data-ATS
or
aws iot describe-domain-configuration –-domain-configuration-name "domain_configuration_name"
```

# Authentication

Check your certificate and private key.

```sh
ENDPOINT='Gotten by above command'
openssl s_client -connect ${endpoint}:443 -CAfile CA.pem -cert cert.pem -key privateKey.pem -showcerts 2>&1 </dev/null
```

## SNI (Server name indication) of TLS extension

**To use features such as multi-account registration, custom domains, and VPC endpoints, you must use the SNI extension.**

# Authorization

AWS IoT resources use AWS IoT Core policies to authorize those resources to perform actions.

```sh
aws iot get-effective-policies --thing-name "MyThing" --principal "arn:aws:iot:us-east-1:123456789012:cert/cert-id"
```

Test whether CONNECT is allowed, without touching the device.

```sh
aws iot test-authorization \
  --principal "arn:aws:iot:us-east-1:123456789012:cert/cert-id" \
  --client-id "MyThing" \
  --auth-infos '{"actionType":"CONNECT","resources":["arn:aws:iot:us-east-1:123456789012:client/MyThing"]}'
```

- I received a PUBNACK or SUBNACK response from the broker. What do I do?

- I have an AUTHORIZATION_FAILURE entry in my logs.

  Make sure that there is a policy attached to the certificate you are using to call AWS IoT. All publish/subscribe operations are denied by default.
