#!/usr/bin/env bash

# login to conan bintray
conan user -p "${BINTRAY_KEY}" -r "${CONAN_REPOSITORY_NAME}" "${BINTRAY_USER}"

# upload all related packages
conan upload "*@${CONAN_USER}/${CONAN_CHANNEL}" -r "${CONAN_REPOSITORY_NAME}" --all --confirm
