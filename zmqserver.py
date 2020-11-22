import random
import pyaudio

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

CHUNK_SIZE = 32768 # In bytes.

sampleWidth = 2 # Just for example, get from metadata.
nChannels = 2 # Just for example, get from metadata.
frameRate = 44100 # Just for example, get from metadata.
frameSize = sampleWidth * nChannels

chunkFrameCount = CHUNK_SIZE / frameSize
chunkTime = chunkFrameCount / frameRate # Time elapsed in one chunk. In seconds.

# Get the number of chunks needed to create 3 seconds audio bytes.
chunkCount = 0
while chunkCount * chunkTime < 3:
    chunkCount += 1

# Generate some random chunks.
randomChunks = []
for _ in range(chunkCount):
    randomChunk = bytearray()
    for _ in range(CHUNK_SIZE):
        randomBits = random.getrandbits(8)
        randomByte = randomBits.to_bytes(1, 'little')
        randomChunk += randomByte
    randomChunks.append(randomChunk)

i = 0
while True:
    #  Do some 'work'
    time.sleep(1)

    socket.send(randomChunks[i])
    print('Send ' + str(i))
    i += 1
    i %= len(randomChunks)