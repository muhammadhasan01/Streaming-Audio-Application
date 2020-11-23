import random
import pyaudio
import sys

import time
import zmq
from wavhandler import play_wav_audio, get_metadata_audio

def create_socket(port):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:{}".format(port))
    return socket

def main():
    port = sys.argv[1]
    wav_file_path = sys.argv[2]

    # print("port: {}".format(port))
    # print("wav_file_path: {}".format(wav_file_path))

    socket = create_socket(port)
    metadata = get_metadata_audio(wav_file_path)
    # print("metadata: {}".format(metadata))

    sampleWidth = metadata["sample_width"]
    nChannels = metadata["num_channels"]
    frameRate = metadata["sample_rate"]
    frameSize = sampleWidth * nChannels

    chunkFrameCount = CHUNK_SIZE / frameSize
    chunkTime = chunkFrameCount / frameRate

    chunkCount = 0
    while chunkCount * chunkTime < 3:
        chunkCount += 1

    # Generate chunks from audio file.
    chunks = []
    for _ in range(chunkCount):
        chunk = bytearray()
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



if __name__ == "__main__":
    main()




# CHUNK_SIZE = 32768 # In bytes.

# sampleWidth = 2 # Just for example, get from metadata.
# nChannels = 2 # Just for example, get from metadata.
# frameRate = 44100 # Just for example, get from metadata.
# frameSize = sampleWidth * nChannels

# chunkFrameCount = CHUNK_SIZE / frameSize
# chunkTime = chunkFrameCount / frameRate # Time elapsed in one chunk. In seconds.

# # Get the number of chunks needed to create 3 seconds audio bytes.
# chunkCount = 0
# while chunkCount * chunkTime < 3:
#     chunkCount += 1

# # Generate some random chunks.
# randomChunks = []
# for _ in range(chunkCount):
#     randomChunk = bytearray()
#     for _ in range(CHUNK_SIZE):
#         randomBits = random.getrandbits(8)
#         randomByte = randomBits.to_bytes(1, 'little')
#         randomChunk += randomByte
#     randomChunks.append(randomChunk)

# i = 0
# while True:
#     #  Do some 'work'
#     time.sleep(1)

#     socket.send(randomChunks[i])
#     print('Send ' + str(i))
#     i += 1
#     i %= len(randomChunks)