| 1   | 2              | 3                | 4                           | 5          |
| --- | -------------- | ---------------- | --------------------------- | ---------- |
| 1   | AWS            | Yes              | ahead of devices connecting | Needed     |
| 2   | AWS            | Yes              | ahead of devices connecting | Needed     |
| 3   | customer       | No               | ahead of devices connecting | Needed     |
| 4   | customer       | No               | ahead of devices connecting | Needed     |
| 5   | customer       | No               | when a customer use devices | Needed     |
| 6   | customer       | No               | when a customer use devices | Needed     |
| 7   | AWS / customer | Yes \*1 / No \*2 | when a customer use devices | Not needed |
| 8   | AWS / customer | Yes \*1 / No \*2 | when a customer use devices | Not needed |

- \*1...When a customer receives a device certificate and a secret key from AWS IoT Core using `CreateKeysAndCertificate` API.
- \*2...When a customer receives a device certificate from CSR using `CreateCertificateFromCsr` API.

1. Use case number. See the details below.
2. certificate authority management
3. Whether if a secret key is passed through the Internet or not.
4. When a customer provision devices.
5. If individual certificates are needed to be set when devices are created.
6. Use cases

## Use cases

1. IoT Core publishes a device certificate and generates a secret key.

   Developing phase not production environment

2. IoT Core publishes a device certificate.

   Provisioning by AWS CA in advance

3. Register a CA certificate and device certificate in advance.

   Provisioning by customer CA in advance

4. Register a device certificate in advance.

   Use secured element where a certificate is embedded.

5. Just in time provisioning

   Auto provisioning only those devices a customer uses.

6. Just in time Registration

   Auto provisioning only those devices a customer uses.
   And provide custom auth mechanism.

7. Fleet provisioning by claiming

   If a customer can't embed a device certificate to a device when it's created.

8. Fleet provisioning by a user

   If a customer can't embed a device certificate to a device when it's created.
