#!/bin/bash
set -e -x

# Install a system package required by our library
yum install -y atlas-devel \
    boost boost-devel boost-python boost-python-devel

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install pytest pytest-runner pytest-xdist # -r /io/dev-requirements.txt
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Install packages and test
for PYBIN in /opt/python/*/bin/; do
    "${PYBIN}/pip" install -v fable --no-index -f /io/wheelhouse
    (cd "$HOME"; "${PYBIN}/pytest" -v -n auto fable)
done
