#!/usr/bin/env bash

set -ex

echo "Curling image"
wget ftp://192.168.143.223/freebsd-11-0.img.gz
echo "Image curled"

echo "Decompressing and writing image to disk"
gzip -cd freebsd-11-0.img.gz | dd of=/dev/sdb
echo "Image written to disk"
