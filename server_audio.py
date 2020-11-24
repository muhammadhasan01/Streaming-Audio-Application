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
import json

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
		if self.meta:
			wav_metadata = WavHandler(fpath).get_metadata_audio()
			return bytes(json.dumps(wav_metadata), 'utf-8')
		else:
			return self.chunk

	def send_packet(self):
		data = self.get_data()
		self.sock.sendto(data, self.server_address)

	def stop(self):
		self.stopped = True

	def run(self):
		while not self.stopped:
			self.send_packet()
			print("Packet is being sent to {}.".format(self.server_address))
			break
			# t = 0
			# while t < const.RESEND_TIMER:
			# 	t += const.RESEND_TIMER_TICK
			# 	time.sleep(const.RESEND_TIMER_TICK)
			# 	if self.stopped:
			# 		print("Packet #{} not restarting...".format(self.sequence))
			# 		break
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
		# chunkTime = 1000
		print("chunkTime: {} ms".format(chunkTime))
		i = 0
		for chunk in self.chunks:
			print("Start sending chunks {}".format(i))
			startTime = time.time()
			sending_threads = [
				#TODO benerin SenderThread
				SenderThread(fpath=self.fpath, server_address=subscriber, chunk=chunk, final=False, meta=False) for subscriber in self.subscribers
			]
			print("Number of subs in step {}: {}".format(i, len(self.subscribers)))
			print("Number of active threads in step {}: {}".format(i, len(sending_threads)))
			for t in sending_threads:
				t.start()
			for t in sending_threads:
				t.join()
			endTime = time.time()
			delta = endTime - startTime
			if delta < chunkTime/1000:
				time.sleep(chunkTime/1000 - delta) # Sleep for the remaining time if there is any.
			# Continue to next chunk
			print("Finished sending chunks {}".format(i))
			i += 1

def send(chunk, subscriber):
	"""
	chunk: data
	subscriber: IP address subscriber
	"""
	# TODO: bikin send buat StreamThread
		# while True:
    # 	s.send(chunk)

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
		print("Listener Bind {}".format(listener_bind))
		self.sock.bind(listener_bind)
		self.stream_thread = stream_thread

	
	def run(self):
		dbg = 0
		while True:
			if dbg == 5:
				break
			p, address = self.sock.recvfrom(const.MAX_PACKET_LENGTH)
			# TODO: Ngirim paket metadata
			
			s_thread = SenderThread(fpath=self.fpath, server_address=address, chunk=[], final=False, meta=True)
			s_thread.start()
			s_thread.join()
			add_subscriber(self.stream_thread, address)

			print("Metadata: {}".format(self.metadata))
			print("Message from client: {}".format(p.decode('utf-8')))
			print("Receiver address: {}".format(address))
			
			dbg += 1
			# break
			# self.sock.sendto(, address)
			# TODO: Add subscriber

# def get_ip():
# 	return str([(
# 		s.connect(('8.8.8.8', 80)),
# 		s.getsockname()[0],
# 		s.close()) 
# 	for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])

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
	# port2 = int(sys.argv[3])
	fpath = sys.argv[2]
			
	wav = WavHandler(fpath)
	metadata = wav.metadata
	print("Metadata: {}".format(metadata))
	RECV_PORT = int(input("Input port of receivers: "))

	stream_thread = StreamThread(fpath=fpath, subscribers=[])

	print("Listening to subscribe request...")
	listener_thread = ListenerThread(fpath=fpath, stream_thread=stream_thread, port=port)
	listener_thread.start()

	print("Start sending audio packets...")
	stream_thread.start()
	print("Pretest Passed")