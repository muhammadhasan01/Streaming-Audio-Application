import socket
import file_handler
import packet
import const

# RECEIVER

def recv_packet(sock):
	data, addr = sock.recvfrom(int(const.MAX_PACKET_LENGTH*1.5))
	p = packet.Packet.to_packet(data)
	return p, addr

def send_packet(sock, p, server_address):
	sock.sendto(p.to_bytes(), server_address)

def get_ip():
	return str([(
		s.connect(('8.8.8.8', 80)),
		s.getsockname()[0],
		s.close()) 
	for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])	

if __name__ == "__main__":

	RECV_IP = get_ip()
	RECV_PORT = int(input("Insert port to bind: "))

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	server_address = (RECV_IP, RECV_PORT)
	sock.bind(server_address)
	
	print("Running on {}:{}".format(RECV_IP, RECV_PORT))

	# initialize File

	f = file_handler.File('downloaded')

	while 1:

		try:
			p, addr = recv_packet(sock)

			if p.p_type == const.TYPE_DATA:
				print("Received DATA for packet #{} from {}, responding with ACK".format(p.p_sequence, addr))
				f.add_chunk(p.p_sequence, p.p_data)
				p = packet.Packet(const.TYPE_ACK, p.p_sequence)
				send_packet(sock, p, addr)

			elif p.p_type == const.TYPE_FIN:
				print("Received FIN for packet #{} from {}, responding with FINACK".format(p.p_sequence, addr))
				f.add_chunk(p.p_sequence, p.p_data)
				p = packet.Packet(const.TYPE_FINACK, p.p_sequence)
				send_packet(sock, p, addr)
				break

			elif p.p_type == const.TYPE_MDATA and const.FILE_METADATA:
				print("Received MDATA from {}, responding with TYPE_MACK".format(addr))
				f.set_name(p.p_data.decode('utf-8'))
				p = packet.Packet(const.TYPE_MACK, p.p_sequence)
				send_packet(sock, p, addr)

			else:
				print("Received unknown packet type.")
				exit(-1)

		except (packet.ChecksumError, packet.LengthError):
			print("Received bad packet, not responding with ACK.")
			continue

	sock.close()

	f.merge_chunks()