import zmq
import pyaudio

context = zmq.Context()

print("Connecting to the server…")
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.subscribe("")

sampleWidth = 2 # Just for example, get from metadata.
nChannels = 2 # Just for example, get from metadata.
frameRate = 44100 # Just for example, get from metadata.

pAudio = pyaudio.PyAudio()
stream = pAudio.open(
    format=pAudio.get_format_from_width(sampleWidth),
    channels=nChannels,
    rate=frameRate,
    output=True,
)

for request in range(10):
    message = socket.recv()

    stream.write(message)
    print("Received %sth " % (request))