#!/bin/bash
set -e

ALLOWED_BINARIES="grep ls cat more less shuf cut sort uniq head tail ed sed wc [ [[ test echo false true"

mkdir -p /tmp/bin
ln -s /usr/bin/* /tmp/bin/
ln -s /bin/* /tmp/bin/

mkdir -p /run/bin
for binary in $ALLOWED_BINARIES; do
    mv "/tmp/bin/$binary" /run/bin;
done

rm -rf /tmp/bin
