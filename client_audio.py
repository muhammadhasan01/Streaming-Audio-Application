import sys 
import pyaudio
import socket

IPAdress = "192.168.0.103"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(bytes("Test", "utf-8"), IPAdress)
