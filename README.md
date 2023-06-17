# AWS IoT Core

# Set up certificates, which contain CA Certificate and X.509, and then deploy AWS IoT Core and AWS Lambda

```sh
. set_up.sh
```

# Execute source codes on devices

## export AWS IoT endpoint as an environment value

```sh
# The command shown below will help you know the IoT Endpoint with CLI.
export AWS_IOT_CORE_ENDPOINT=$(aws iot describe-endpoint \
  --endpoint-type iot:Data-ATS \
  --query endpointAddress \
  --output text)
```

## cpp

```sh
cd Device/cpp
# build source code using cmake
. build.sh
# execute program
./main
```
