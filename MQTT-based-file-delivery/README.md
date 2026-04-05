1. Create a file and upload to the S3.

Replace `<Your S3 bucket>` with your own bucket.

```sh
dd if=/dev/zero of=IoTStream bs=4096 count=1
aws s3 cp IoTStream s3://<Your S3 bucket>/IoT/IoTStream
```

2. Modify create-stream.json file for your own.

Specify the S3 bucket used above and the key.
Replace `roleArn` with your own

3. Create a stream

```sh
aws iot create-stream --cli-input-json file://create-stream.json
```
