#!/usr/bin/env bash

SOURCE_DIR=/opt/work

mkdir -p build
cd build

# build
cmake -DCMAKE_PREFIX_PATH="/opt/work" -DCMAKE_BUILD_TYPE="Release" ..
cmake --build . --config "Release"
cd src
