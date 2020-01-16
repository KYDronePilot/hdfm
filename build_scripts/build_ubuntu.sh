#!/usr/bin/env bash

# Build script for hdfm on Ubuntu

# Overridable vars
PYTHON=${PYTHON-python3.7}

# Local variables
ABS_PATH=`realpath "${0}"`
DIR=`dirname ${ABS_PATH}`
export PROJECT_PATH=${DIR}/..
VENV=${PROJECT_PATH}/venv
PIP=${VENV}/bin/pip
PYINSTALLER=${VENV}/bin/pyinstaller
REQUIREMENTS=${PROJECT_PATH}/requirements.txt
BUILD=${PROJECT_PATH}/build
DIST=${PROJECT_PATH}/dist
SPEC=${PROJECT_PATH}/utils/pyinstaller_ubuntu.spec

# Create virtualenv if one does not exist
if [ ! -d ${VENV} ]; then
    ${PYTHON} -m venv ${VENV}
fi

# Install requirements
${PIP} install -r ${REQUIREMENTS}

# Delete PyInstaller build/dist dirs
if [ -d ${BUILD} ]; then
    rm -rf ${BUILD}
fi
if [ -d ${DIST} ]; then
    rm -rf ${DIST}
fi

# Build with PyInstaller
${PYINSTALLER} ${SPEC}
