# You might need to register your certificate authority (CA) with AWS IoT if you are using client certificates signed by a CA that AWS IoT doesn't recognize.

[See details on AWS docs](https://docs.aws.amazon.com/iot/latest/developerguide/manage-your-CA-certs.html)

# Generate certificates using CLI

1. Create a `SNI_ONLY` CA certificate or `DEFAULT` CA certificate.

- SNI_ONLY

```sh
. ca_sni_only.sh
```

- DEFAULT

```sh
. ca_default.sh
```

2. Create a client certificate

```sh
. client_cli.sh
```
