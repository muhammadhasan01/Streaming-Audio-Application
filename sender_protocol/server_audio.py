import os
import socket
import time
import threading
import math
import packet
import const
from collections import deque
from wavhandler import WavHandler

class SenderThread(threading.Thread):

	def __init__(self, sock, server_address, fname, sequence, final=False, meta=False):
		super(SenderThread, self).__init__()
		self.sock = sock
		self.server_address = server_address
		self.fname = fname
		self.sequence = sequence
		self.final = final
		self.meta = meta
		self.stopped = False

	def get_data(self):
		if self.meta:
			data = fname.encode('utf-8')
		else:
			offset = self.sequence * const.MAX_LENGTH
			f = open(self.fname, 'rb')
			f.seek(offset)
			data = f.read(const.MAX_LENGTH)
			f.close()

		return data

	def send_packet(self):
		data = self.get_data()
		if self.final:
			p = packet.Packet(const.TYPE_FIN, self.sequence, data)
		elif self.meta:
			p = packet.Packet(const.TYPE_MDATA, self.sequence, data)
		else:
			p = packet.Packet(const.TYPE_DATA, self.sequence, data)

		self.sock.sendto(p.to_bytes(), self.server_address)

	def stop(self):
		self.stopped = True

	def run(self):
		while not self.stopped:
			self.send_packet()
			print("Packet #{} is being sent to {}.".format(self.sequence, self.server_address))

			t = 0
			while t < const.RESEND_TIMER:
				t += const.RESEND_TIMER_TICK
				time.sleep(const.RESEND_TIMER_TICK)
				if self.stopped:
					print("Packet #{} not restarting...".format(self.sequence))
					break
# SENDER

class StreamThread(threading.Thread):

	def __init__(self, fpath, subscribers=[]):
		self.fpath = fpath;
		self.wav = WavHandler(fpath)
		self.subscribers = subscribers
		self.chunks = self.wav.chunks
		self.chunk_size = len(self.chunks)
	
	def add_subscriber(self, subscriber):
    	self.subscribers.append(subscriber)
	
	def run(self):
		# TODO: get from metadata
		nChannels = self.wav.metadata["num_channels"] # Audio channel count
		sampleWidth = self.wav.metadata["sample_width"]  # Audio sample width
		frameRate = self.wav.metadata["sample_rate"] # Audio frame rate

		frameSize = nChannels * sampleWidth # In bytes
		frameCountPerChunk = CHUNK_SIZE / frameSize

		chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.
		nChannels = self.wav.metadata["num_channels"] # Audio channel count
		sampleWidth = self.wav.metadata["sample_width"]  # Audio sample width
		frameRate = self.wav.metadata["sample_rate"] # Audio frame rate

		frameSize = nChannels * sampleWidth # In bytes
		frameCountPerChunk = CHUNK_SIZE / frameSize

		chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.
		nChannels = self.wav.metadata["num_channels"] # Audio channel count
		sampleWidth = self.wav.metadata["sample_width"]  # Audio sample width
		frameRate = self.wav.metadata["sample_rate"] # Audio frame rate

		frameSize = nChannels * sampleWidth # In bytes
		frameCountPerChunk = CHUNK_SIZE / frameSize

		chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.
		nChannels = self.wav.metadata["num_channels"] # Audio channel count
		sampleWidth = self.wav.metadata["sample_width"]  # Audio sample width
		frameRate = self.wav.metadata["sample_rate"] # Audio frame rate

		frameSize = nChannels * sampleWidth # In bytes
		frameCountPerChunk = CHUNK_SIZE / frameSize

		chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.
		nChannels = self.wav.metadata["num_channels"] # Audio channel count
		sampleWidth = self.wav.metadata["sample_width"]  # Audio sample width
		frameRate = self.wav.metadata["sample_rate"] # Audio frame rate

		frameSize = nChannels * sampleWidth # In bytes
		frameCountPerChunk = CHUNK_SIZE / frameSize

		chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.

		for chunk in self.chunks:
			startTime = time.time()
			sending_threads = [
				#TODO benerin SenderThread
				SenderThread(chunk) for subscriber in subscribers
			]
			for t in sending_threads:
				t.start()
			for t in sending_threads:
				t.join()
			endTime = time.time()
			delta = endTime - startTime
			if delta < chunkTime:
    			time.sleep(chunkTime - delta) # Sleep for the remaining time if there is any.
			# Continue to next chunk

def send(chunk, subscriber):
	"""
	chunk: data
	subscriber: IP address subscriber
	"""
	# TODO: bikin send buat StreamThread
	pass 


def add_subscriber(stream_thread, subscriber):
    """
	stream_thread: thread for streaming
	subscriber: IP address for new subscriber
	"""
    stream_thread.add_subscriber(subscriber)



class ListenerThread(threading.Thread):

	def __init__(self, fpath, stream_thread):
		self.fpath = fpath
		self.wav = WavHandler(fpath)
		self.metadata = self.wav.metadata
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.stream_thread = stream_thread

		self.total_threads_pool = deque()

		if const.FILE_METADATA:
			self.total_threads_pool.append(
				SenderThread(self.sock, self.server_address, self.fname, 0, meta=True)	
			)

		for i in range(self.total_chunks-1):
			self.total_threads_pool.append(
				SenderThread(self.sock, self.server_address, self.fname, i, final=False)	
			)

		self.final = SenderThread(self.sock, self.server_address, self.fname, total_chunks-1, final=True)

	def run(self):
		while True:
			p, address = self.sock.recvfrom(const.MAX_LENGTH)
			# TODO: Ngirim paket metadata
			
			# TODO: Add subscriber
			add_subscriber(self.stream_thread, address)


def recv_packet(sock):
	data, addr = sock.recvfrom(const.MAX_PACKET_LENGTH)
	p = packet.Packet.to_packet(data)
	return p, addr

def get_file_size(path):
	return os.stat(path).st_size

def get_file_chunks(path):
	return math.ceil(get_file_size(path)/const.MAX_LENGTH)

def to_addresses(addresses, port):
	server_addresses = []
	for address in addresses:
		server_addresses.append((address, port))
	return server_addresses

if __name__ == "__main__":

	port = sys.argv[1]
	fpath = sys.argv[2]
			
	wav = WavHandler(fpath)
	metadata = wav.metadata
	RECV_PORT = int(input("Input port of receivers: "))

	stream_thread = StreamThread(fpath=fpath, subscribers=[])
	
	print("Listening to subscribe request...")
	listener_thread = ListenerThread(fpath=fpath, stream_thread=stream_thread)
	listener_thread.start()

	print("Start sending audio packets...")
	stream_thread.start()