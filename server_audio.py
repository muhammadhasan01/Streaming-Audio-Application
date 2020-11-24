import os
import sys
import socket
import time
import threading
import math
import sender_protocol.packet as packet
import sender_protocol.const as const
from collections import deque
from wavhandler import WavHandler

class SenderThread(threading.Thread):

	def __init__(self, fpath, server_address, chunk, final=False, meta=False):
		super(SenderThread, self).__init__()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_address = server_address
		self.chunk = chunk
		self.final = final
		self.meta = meta
		self.stopped = False

	def get_data(self):
		# if self.meta:
    	# 	return
		# else:
		return self.chunk

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

	def __init__(self, fpath, subscribers):
		super(StreamThread, self).__init__()
		self.fpath = fpath;
		self.wav = WavHandler(fpath)
		self.subscribers = subscribers
		self.chunks = self.wav.chunks
		self.chunk_size = len(self.chunks)
		self.metadata = self.wav.get_metadata_audio()
		# self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def add_subscriber(self, subscriber):
		self.subscribers.append(subscriber)

	def run(self):
		nChannels = self.metadata["num_channels"]
		sampleWidth = self.metadata["sample_width"]
		frameRate = self.metadata["sample_rate"]
		
		frameSize = nChannels * sampleWidth # In bytes
		frameCountPerChunk = const.CHUNK_SIZE / frameSize
		
		chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.
		for chunk in self.chunks:
			startTime = time.time()
			sending_threads = [
				#TODO benerin SenderThread
				SenderThread(server_address, chunk) for subscriber in self.subscribers
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

	def __init__(self, fpath, stream_thread, port):
		super(ListenerThread, self).__init__()
		self.fpath = fpath
		self.wav = WavHandler(fpath)
		self.metadata = self.wav.metadata
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		listener_address = socket.gethostbyname(socket.gethostname())
		listener_bind = (listener_address, port)
		self.sock.bind(listener_bind)
		self.stream_thread = stream_thread

	def run(self):
		while True:
			p, address = self.sock.recvfrom(const.MAX_PACKET_LENGTH)
			# TODO: Ngirim paket metadata
			print("Metadata: ".format(self.metadata))
			print("Receiver address: ".format(address))
			break
			# self.sock.sendto(, address)
			# TODO: Add subscriber
			# add_subscriber(self.stream_thread, address)

def get_ip():
	return str([(
		s.connect(('8.8.8.8', 80)),
		s.getsockname()[0],
		s.close()) 
	for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])

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

	port = int(sys.argv[1])
	fpath = sys.argv[2]
			
	wav = WavHandler(fpath)
	metadata = wav.metadata
	RECV_PORT = int(input("Input port of receivers: "))

	stream_thread = StreamThread(fpath=fpath, subscribers=[])

	print("Listening to subscribe request...")
	listener_thread = ListenerThread(fpath=fpath, stream_thread=stream_thread, port=port)
	listener_thread.start()

	print("Start sending audio packets...")
	stream_thread.start()