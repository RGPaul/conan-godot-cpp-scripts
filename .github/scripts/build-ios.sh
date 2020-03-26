#!/usr/bin/env bash
# ----------------------------------------------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2018-2020 Ralph-Gordon Paul. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ----------------------------------------------------------------------------------------------------------------------

set -e

declare ARCH=$1
declare BUILD_TYPE=$2

export IOS_SDK_VERSION=$(xcodebuild -showsdks | grep iphoneos | awk '{print $4}' | sed 's/[^0-9,\.]*//g');
echo "iOS SDK ${IOS_SDK_VERSION}";

#=======================================================================================================================
# create package for architecture and build type
      
conan create . ${CONAN_PACKAGE_NAME}/${LIBRARY_VERSION}@${CONAN_USER}/${CONAN_CHANNEL} -s os=iOS \
    -s os.version=${IOS_SDK_VERSION} -s arch=$ARCH -s build_type=$BUILD_TYPE -o shared=False

#=======================================================================================================================
# create zip file from package contents

declare BUILD_TYPE_LOWER="$(echo ${BUILD_TYPE} | tr '[:upper:]' '[:lower:]')"
declare ZIP_FILENAME="godot-cpp-${LIBRARY_VERSION}-ios-${ARCH}-${BUILD_TYPE_LOWER}.zip"

mkdir deps || true
mkdir output || true

conan install .github/conan ${CONAN_PACKAGE_NAME}/${LIBRARY_VERSION}@${CONAN_USER}/${CONAN_CHANNEL} -s os=iOS \
    -s os.version=${IOS_SDK_VERSION} -s arch=$ARCH -s build_type=$BUILD_TYPE

cd deps
zip -r "../output/${ZIP_FILENAME}" *
