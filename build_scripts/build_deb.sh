#!/usr/bin/env bash
# Build deb package

DEB_ROOT=$2
EXECUTABLE=$3
BUILD_DIR=$4

# Substitute env vars
sed -i "s/{arch}/${BUILD_ARCH}/g" ${DEB_ROOT}/DEBIAN/control

# Copy executable
cp ${EXECUTABLE} ${DEB_ROOT}/usr/local/bin

# Build package
chmod 775 ${DEB_ROOT}/DEBIAN/postinst
dpkg-deb --build ${DEB_ROOT} ${BUILD_DIR}/hdfm.deb
