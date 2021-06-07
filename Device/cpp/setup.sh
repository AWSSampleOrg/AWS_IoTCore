#!/bin/bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)

mkdir -p build && cd build
cmake -DCMAKE_INSTALL_PREFIX=${SOURCE_DIR} -DBUILD_DEPS=ON -DCMAKE_BUILD_TYPE="Release" ../aws-iot-device-sdk-cpp-v2
cmake --build . --target install --config "Release"
