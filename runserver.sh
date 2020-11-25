#!/bin/bash

# Script to run server
# $1 is the port to bind the server with (example: 5555)
# $2 is the path file to wav audio (example: ./sample_wav/test1.wav)
# Running Exampe: runserver.sh 5555 ./sample_wav/hallking.wav

python server_audio.py "$1" "$2" 5555 ./sample_wav/hallking.wav