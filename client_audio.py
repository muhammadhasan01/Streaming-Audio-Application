import sys 
import pyaudio
import socket
import sender_protocol.const as const
import json

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

    # Prepare the audio player.
    audio_buffer = []
    pAudio = pyaudio.PyAudio()
    stream = pAudio.open(
        format=pAudio.get_format_from_width(dictionary_meta_data["sample_width"]),
        channels=dictionary_meta_data["num_channels"],
        rate=dictionary_meta_data["sample_rate"],
        output=True,
    )
    
    # for chunk in randomChunks:
    #     stream.write(bytes(chunk))

    #TODO: receive data and play, or store to buffer (array)
    # while True:
    #     if (!False):
    #         chunk, server_address = s.recvfrom(const.MAX_PACKET_LENGTH)
    #         # buffer_audio.append(chunk)
    #         stream.write(chunk)
    #         #terima