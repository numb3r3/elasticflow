#!/usr/bin/env bash

set -e  # fail and exit on any command erroring

SRC_NAME=flow.proto
SRC_DIR=../elasticflow/proto/
VER_FILE=../elasticflow/__init__.py

printf "\e[1;33mgenerating protobuf python interface\e[0m\n"

protoc -I ${SRC_DIR} --python_out=${SRC_DIR}  ${SRC_DIR}${SRC_NAME}

# update protobuf version in gnes/__init__.py

OLDVER=$(sed -n 's/^__proto_version__ = '\''\(.*\)'\''$/\1/p' $VER_FILE)
printf "current proto version:\t\e[1;33m$OLDVER\e[0m\n"

NEWVER=$(echo $OLDVER | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{$NF=sprintf("%0*d", length($NF), ($NF+1)); print}')
printf "bump proto version to:\t\e[1;32m$NEWVER\e[0m\n"

sed -i '' -e 's/^__proto_version__ = '\''\(.*\)'\''/__proto_version__ = '\'"$NEWVER"\''/' $VER_FILE
printf "\e[1;32mAll done!\e[0m\n"