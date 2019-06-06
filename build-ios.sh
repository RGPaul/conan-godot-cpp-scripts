#!/usr/bin/env bash
# ----------------------------------------------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2019 Ralph-Gordon Paul. All rights reserved.
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

#=======================================================================================================================
# settings

declare CONAN_USER=rgpaul
declare CONAN_CHANNEL=stable

declare LIBRARY_VERSION=20190605
declare IOS_SDK_VERSION=$(xcodebuild -showsdks | grep iphoneos | awk '{print $4}' | sed 's/[^0-9,\.]*//g')

#=======================================================================================================================
# create conan package

function createConanPackage()
{
    local arch=$1
    local build_type=$2

    conan create . godot-cpp/${LIBRARY_VERSION}@${CONAN_USER}/${CONAN_CHANNEL} -s os=iOS \
        -s os.version=${IOS_SDK_VERSION} -s arch=${arch} -s build_type=${build_type} -o shared=False
}

#=======================================================================================================================
# create packages for all architectures and build types

# iOS (any arm arch will build fat libraries with armv7, armv7s and armv8 and set arch to 'AnyARM')
createConanPackage armv8 Release
createConanPackage armv8 Debug
# SIMULATOR
createConanPackage x86_64 Debug
