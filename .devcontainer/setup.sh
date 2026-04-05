#!/usr/bin/env bash

SOURCE_DIR=/opt/work

cd ${SOURCE_DIR}
git clone --recursive https://github.com/aws/aws-iot-device-sdk-cpp-v2.git
# Ensure all submodules are properly updated
cd aws-iot-device-sdk-cpp-v2
git submodule update --init --recursive
cd ..
# Make a build directory for the SDK. Can use any name.
# If working with multiple SDKs, using a SDK-specific name is helpful.
mkdir -p build && cd build
cmake -DCMAKE_INSTALL_PREFIX=${SOURCE_DIR} -DBUILD_DEPS=ON -DCMAKE_BUILD_TYPE="Release" ../aws-iot-device-sdk-cpp-v2
cmake --build . --target install --config "Release"
