#! /bin/bash

set -e

echo -e "[INFO]==========Decompression tar package=========="
tar -xvf unichain.tar
echo -e "[INFO]==========Done=========="
echo -e "  "

echo -e "[INFO]==========Decompression tar package=========="
tar -xvf deb.tar
echo -e "[INFO]==========Done=========="
echo -e "  "

exit 0
