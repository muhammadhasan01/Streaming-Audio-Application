# Tugas Besar 2 Jaringan Komputer (IF3130) - Simple Audio Streaming Application

Simple Audio Streaming Application is an application to stream audio file especially wav file from a server to multiple clients made with Python

## How to Run

To run this application on a terminal you can use the script that we made:

```sh
runserver.sh <PORT> <PATH_TO_AUDIO_FILE>
runclient.sh <IPADRESS_SERVER>
```

Here is an example:

```sh
runserver.sh 5555 ./sample_wav/hallking.wav
runclient.sh 192.168.1.46
```

**Note**: <br/>
To find your own IPAddress server you can type in `ipconfig/all` on a terminal and find the value of **IPv4 Address**.

## Contributors
| Name              | NIM      |
|---------------------------|----------|
| Muhammad Hasan            | 13518012 |
| Farras Mohammad Hibban Faddila       | 13518017 |
| Fabian Zhafransyah   | 13518022 |
| Ilham Syahid Syamsudin | 13518028 |
