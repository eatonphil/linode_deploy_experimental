#!/usr/bin/env bash

set -ex

echo "Curling image"
wget ftp://192.168.143.223/$1.img.gz
echo "Image curled"

echo "Decompressing and writing image to disk"
gzip -cd $1.img.gz | dd of=/dev/sdb bs=1M
echo "Image written to disk"
