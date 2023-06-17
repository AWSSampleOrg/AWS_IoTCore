#!/usr/bin/env bash

SOURCE_DIR=/opt/work

mkdir -p build
cd build

# build
if [ -z "${AWS_IOT_CORE_ENDPOINT}" ] ; then
    echo 'export AWS_IOT_CORE_ENDPOINT="**Check your own IoT Core endpoint**"'
    # The command shown below will help you know the IoT Endpoint with CLI.
    # export AWS_IOT_CORE_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS \
    #   --query endpointAddress \
    #   --output text)
fi
cmake -DCMAKE_PREFIX_PATH="/opt/work" -DCMAKE_BUILD_TYPE="Release" ..
cmake --build . --config "Release"
cd src
