https://docs.aws.amazon.com/iot/latest/developerguide/transfer-cert.html

Both `AWS published certificates` and `User published certificates` can be transferred.

# AWS account which transfers its client certificate to another AWS account.

```sh
aws iot update-certificate --certificate-id certificateId --new-status INACTIVE
aws iot list-attached-policies --target certificateArn
aws iot detach-policy --target certificateArn --policy-name policy-name
aws iot list-principal-things --principal certificateArn
aws iot detach-thing-principal --principal certificateArn --thing-name thing-name
```

Transfer to another account

```sh
aws iot transfer-certificate --certificate-id certificateId --target-aws-account account-id
```

Cancel a certificate transfer

```sh
aws iot cancel-certificate-transfer --certificate-id certificateId
```

# AWS account which accepts/denies a certificate transfer.

Accept

```sh
aws iot accept-certificate-transfer --certificate-id certificateId
```

Reject

```sh
aws iot reject-certificate-transfer --certificate-id certificateId
```
