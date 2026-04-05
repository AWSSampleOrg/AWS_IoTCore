# If you want to use your certificates in multiple AWS accounts in a region

- Transfer method can be used with both `AWS published certificates` and `Transfer a certificate to another account`.

## 1. AWS published certificates

Look at ./transfer-client-certificate.md

[Transfer a certificate to another account](https://docs.aws.amazon.com/iot/latest/developerguide/transfer-cert.html)

## 2. User published certificates

### Transfer a certificate to another account

Look at ./transfer-client-certificate.md

[Transfer a certificate to another account](https://docs.aws.amazon.com/iot/latest/developerguide/transfer-cert.html)

### Multi-account registration

[Using X.509 client certificates in multiple AWS accounts with multi-account registration
](https://docs.aws.amazon.com/iot/latest/developerguide/x509-client-certs.html#multiple-account-cert)

1. You can register the device certificates with a CA. You can register the signing CA in multiple accounts in SNI_ONLY mode and use that CA to register the same client certificate to multiple accounts. For more information, see [Register a CA certificate in SNI_ONLY mode (CLI) - Recommended](https://docs.aws.amazon.com/iot/latest/developerguide/manage-your-CA-certs.html#register-CA-cert-SNI-cli).

2. You can register the device certificates without a CA. See [Register a client certificate signed by an unregistered CA (CLI)](https://docs.aws.amazon.com/iot/latest/developerguide/manual-cert-registration.html#manual-cert-registration-noca-cli). Registering a CA is optional. You're not required to register the CA that signed the device certificates with AWS IoT.
