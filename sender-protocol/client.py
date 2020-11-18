import os
import socket
import time
import threading
import math
import packet
import const
from collections import deque

# SENDER

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


class ConnectorThread(threading.Thread):

	def __init__(self, server_address, fname, total_chunks):
		super(ConnectorThread, self).__init__()
		self.server_address = server_address
		self.fname = fname
		self.total_chunks = total_chunks
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# initialize threads pool

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

		# run threads MAX_SENDER_THREADS at a time

		running_threads_pool = []

		i = 0
		while self.total_threads_pool and i<const.MAX_SENDER_THREADS:
			t = self.total_threads_pool.popleft()
			t.start()
			running_threads_pool.append(t)
			i += 1

		# receive ACKs

		while running_threads_pool:
			try:
				p, addr = recv_packet(self.sock)
				assert p.p_type in [const.TYPE_ACK, const.TYPE_MACK]
				
				new = []
				for t in running_threads_pool:
					if t.sequence == p.p_sequence:
						t.stop()
					else:
						new.append(t)

				running_threads_pool = new
				
				if self.total_threads_pool:
					t = self.total_threads_pool.popleft()
					t.start()
					running_threads_pool.append(t)

			except (packet.ChecksumError, packet.LengthError):
				print("Received bad packet, not stopping resend.")
				continue

		# FIN

		self.final.start()

		while not self.final.stopped:
			try:
				p, addr = recv_packet(self.sock)
				assert p.p_type == const.TYPE_FINACK
				assert p.p_sequence == self.final.sequence
				self.final.stop()
			except (packet.ChecksumError, packet.LengthError):
				print("Received bad packet, not stopping resend.")
				continue


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

	IPs = input("Input receiver address(es): ").split(',')
	RECV_PORT = int(input("Input port of receivers: "))

	server_addresses = to_addresses(IPs, RECV_PORT)

	fname = input("Input path of file to send: ")

	total_chunks = get_file_chunks(fname)

	conn_threads = [
		ConnectorThread(address, fname, total_chunks)
		for address in server_addresses
	]

	print("Starting send...")

	if const.MULTITHREADED:
		for t in conn_threads:
			t.start()
		for t in conn_threads:
			t.join()
	else:
		for t in conn_threads:
			t.start()
			t.join()

	print("Finished sending to all receivers.")