import sys 
import pyaudio
import socket
import sender_protocol.const as const
import json
import threading

def add_chunk(player_thread, chunk):
    player_thread.add_chunk(chunk)

class PlayerThread(threading.Thread):
    def __init__(self, dictionary_meta_data):
        super(PlayerThread, self).__init__()
        # self.chunk = chunk
        pAudio = pyaudio.PyAudio()
        self.stream = pAudio.open(
            format=pAudio.get_format_from_width(dictionary_meta_data["sample_width"]),
            channels=dictionary_meta_data["num_channels"],
            rate=dictionary_meta_data["sample_rate"],
            output=True,
        )
        self.audio_buffer = []
        self.is_stopped = False
    
    def stop(self):
        self.is_stopped = True

    def run(self):
        idx = 0
        while not self.is_stopped:
            if len(self.audio_buffer) > idx:
                self.stream.write(self.audio_buffer[idx])
                idx += 1
    
    def add_chunk(self, chunk):
        self.audio_buffer.append(chunk)

class DownloaderThread(threading.Thread):
    def __init__(self, sock, player_thread):
        super(DownloaderThread, self).__init__()
        self.sock = sock
        self.player_thread = player_thread
    
    def run(self):
        while True:
            chunk, address = self.sock.recvfrom(const.MAX_PACKET_LENGTH)
            if (chunk == bytes("BerhentiDong", "utf-8")):
                self.player_thread.stop()
                break
            add_chunk(self.player_thread, chunk)

if __name__== "__main__":
    send_bind = ("192.168.56.1", 5555)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Start sending packet to server...")
    s.sendto(bytes("Haiii", "utf-8"), ("192.168.56.1", 5555))
    bytes_meta_data, server_address = s.recvfrom(const.MAX_PACKET_LENGTH)

    #Convert meta_data received from server to variable
    dictionary_meta_data = json.loads(bytes_meta_data.decode("utf-8"))
    print("Server address that I subscribed: {}".format(server_address))
    print("Meta data: {}".format(dictionary_meta_data))

    player_thread = PlayerThread(dictionary_meta_data)
    player_thread.start()
    
    downloader_thread = DownloaderThread(s, player_thread)
    downloader_thread.start()

    # for chunk in randomChunks:
    #     stream.write(bytes(chunk))

    # TODO: receive data and play, or store to buffer (array)
    # while True:
    #     if not False:
    #         chunk, server_address = s.recvfrom(const.MAX_PACKET_LENGTH)
    #         # buffer_audio.append(chunk)