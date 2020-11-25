#!/bin/bash

# Script to run client
# $1 is the IPAdress of the server (example: 192.168.1.46)
# Running Exampe: runclient.sh 192.168.1.46

python client_audio.py "$1"