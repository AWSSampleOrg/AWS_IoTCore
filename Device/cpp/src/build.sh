#!/bin/bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)

mkdir -p build
cd build

# build
cmake -DCMAKE_PREFIX_PATH="${SOURCE_DIR%/*}" -DCMAKE_BUILD_TYPE="Release" ..
cmake --build . --config "Release"
