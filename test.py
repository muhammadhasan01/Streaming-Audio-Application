import socket
import pyaudio
import wave
import sys
import pickle
import time

HOST=""
PORT=1061
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 3


def record(sock):   
    def callback_record(in_data, frame_count, time_info, status):
        #print len(in_data)
        sock.sendall(in_data)       

        return (in_data, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    stream_callback=callback_record)

    stream.start_stream()
    return stream

def play(sock):
    def callback_play(in_data, frame_count, time_info, status):
        #msg=recv_all(sock)
        in_data=sock.recv(5000)
        return (in_data, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=False,
                    output=True,
                    stream_callback=callback_play)

    stream.start_stream()
    return stream

def recv_all(sock):
    data=sock.recv(5000)
    return data


if sys.argv[1] == 'server':
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(10)
    while(True):
        print "Listening at:", s.getsockname()
        sc, addr=s.accept()
        print "Connection established with:", addr

        while True:
            stream_record=record(sc)
            #stream_play=play(sc)
            while stream_record.is_active():# or stream_play.is_active():
                #time.sleep(0.0)
                pass
            #stream_record.stop_stream()
            #stream_record.close()
        #stream_play.stop_stream()
        #stream_play.close()

elif sys.argv[1]=='client':
    s.connect((HOST, PORT))
    while True:     
        stream_play=play(s)

        while stream_play.is_active():#stream_record.is_active() or 
            #time.sleep(0.0)
            pass

        #stream_record.stop_stream()
        #stream_record.close()
        #stream_play.stop_stream()
        #stream_play.close()