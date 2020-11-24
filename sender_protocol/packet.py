import sender_protocol.const
import struct

class ChecksumError(Exception):
	pass

class LengthError(Exception):
	pass

class Packet:
	# 0x0 (DATA), 0x1 (ACK), 0x2 (FIN), dan 0x3 (FIN-ACK).

	def __init__(self, p_type, p_sequence, p_data=b''):
		assert p_type in const.AVAILABLE_TYPES
		assert 0 <= len(p_data) <= const.MAX_LENGTH
		assert 0 <= p_sequence <= const.MAX_SEQUENCE

		if p_type in [const.TYPE_ACK, const.TYPE_FINACK]:
			assert len(p_data) == 0

		self.p_type = p_type
		self.p_sequence = p_sequence
		self.p_data = p_data

	def generate_checksum(self, head):

		# pad with \x00
		check_data = head + self.p_data

		if len(check_data) % 2 != 0:
			check_data += b'\x00'

		# xor checksum
		checksum = 0
		for value, in struct.iter_unpack(">H", check_data):
			checksum ^= value

		return checksum

	def to_bytes(self):
		head = b''

		# type 8 bits
		head += struct.pack(">B", self.p_type)

		# length 16 bits
		head += struct.pack(">H", len(self.p_data))

		# sequence 16 bits
		head += struct.pack(">H", self.p_sequence)

		packet = head
		packet += struct.pack(">H", self.generate_checksum(head))
		packet += self.p_data

		return packet

	@classmethod
	def to_packet(cls, raw):
		assert len(raw) >= 7

		# process head
		p_type, p_len, p_sequence, p_checksum = struct.unpack(">BHHH", raw[:7])
		p_data = raw[7:]

		if p_len != len(p_data):
			raise LengthError

		packet = cls(p_type, p_sequence, p_data)

		if p_checksum != packet.generate_checksum(raw[:5]):
			raise ChecksumError

		return packet