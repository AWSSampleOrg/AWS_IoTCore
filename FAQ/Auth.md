# Authentication

1. Supported Authentication

- X.509
- IAM (User, Group, Role)
- [Cognito](https://docs.aws.amazon.com/iot/latest/developerguide/cognito-identities.html)

  ```
  Amazon Cognito Identity creates unauthenticated and authenticated identities. Unauthenticated identities are used for guest users in a mobile or web application who want to use the app without signing in. Unauthenticated users are granted only those permissions specified in the IAM policy associated with the identity pool.

  When you use authenticated identities, in addition to the IAM policy attached to the identity pool, you must attach an AWS IoT policy to an Amazon Cognito Identity. To attach an AWS IoT policy, use the AttachPolicy API and give permissions to an individual user of your AWS IoT application. You can use the AWS IoT policy to assign fine-grained permissions for specific customers and their devices.
  ```

https://docs.aws.amazon.com/iot/latest/developerguide/client-authentication.html

# Authorization
