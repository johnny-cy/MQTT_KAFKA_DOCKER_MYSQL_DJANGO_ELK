#!/bin/sh

BASEDIR=$(dirname "$0")

cd ${BASEDIR}/vagrant && vagrant up
