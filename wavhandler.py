import wave
import sys
import pyaudio  
import sender_protocol.const as const
import math

CHUNK_SIZE = 32767 # In bytes.

class WavHandler():
    def __init__(self, fpath):
        self.max_chunk_size = 1024
        self.fpath = fpath

        self.file = wave.open(fpath, "rb")
        num_frames = self.file.getnframes()
        print(self.file)
        self.metadata = {
            "sample_width": self.file.getsampwidth(),
            "num_channels": self.file.getnchannels(), 
            "sample_rate": self.file.getframerate()
        }
        # self.file = AudioSegment.from_file(file=fpath, format="wav") 

        self.chunks = self.get_chunks_audio()

    def play_wav_audio(self):
        #define stream chunk   
        chunk = 1024

        #open a wav format music  
        f = self.file
        #instantiate PyAudio  
        player = pyaudio.PyAudio()  
        #open stream  
        stream = player.open(format = player.get_format_from_width(f.getsampwidth()),  
                        channels = f.getnchannels(),  
                        rate = f.getframerate(),  
                        output = True)  
        #read data  
        data = f.readframes(chunk)  

        #play stream  
        while data:  
            stream.write(data)  
            data = f.readframes(chunk)  

        #stop stream  
        stream.stop_stream()  
        stream.close()  

        #close PyAudio  
        player.terminate()  

    def get_metadata_audio(self):
        return self.metadata

    def get_chunks_audio(self):
        nChannels = self.metadata["num_channels"]
        sampleWidth = self.metadata["sample_width"]
        frameRate = self.metadata["sample_rate"]

        frameSize = nChannels * sampleWidth # In bytes
        frameCountPerChunk = CHUNK_SIZE / frameSize

        chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.

        # chunks = make_chunks(self.file, chunkTime) #Make chunks of one sec
        chunks = []
        chunks_bytes = self.file.readframes(self.file.getnframes())
        for i in range(math.ceil(len(chunks_bytes)/const.MAX_PACKET_LENGTH)):
            chunk_size = const.MAX_PACKET_LENGTH
            if ((i+1)*chunk_size+44 > len(chunks_bytes)):
                chunks.append(chunks_bytes[i*chunk_size + 44:])
            else:
                chunks.append(chunks_bytes[i*chunk_size + 44:(i+1)*chunk_size + 44])
            print(len(chunks[i]))
        
        print("Length of Chunks: {}".format(len(chunks)))
        print("Chunks: {}".format(chunks_bytes[:5]))
        return chunks

if __name__ == "__main__":
    # port = sys.argv[1]
    # wav_file_path = sys.argv[1]
    wav_file_path = "./sample_wav/test.wav"

    # # print("port: {}".format(port))
    # print("wav_file_path: {}".format(wav_file_path))

    # wav = WavHandler(wav_file_path)

    # metadata = wav.get_metadata_audio()
    # print("metadata: {}".format(metadata))

    # wav.play_wav_audio()

    wavfile = WavHandler(wav_file_path)
    # wavfile.get_chunks_audio()

    # from scipy.io.wavfile import read
    # from pydub import AudioSegment

    # rate, signal = read(wav_file_path)
    # channel1 = signal[:]

    # audio_segment = AudioSegment(
    #     channel1.tobytes(), 
    #     frame_rate=rate,
    #     sample_width=channel1.dtype.itemsize, 
    #     channels=1
    # )

    # # test that it sounds right (requires ffplay, or pyaudio):
    # from pydub.playback import play
    # play(audio_segment)

    # with wave.open(wav_file_path) as fd:
    #     params = fd.getparams()
    #     frames = fd.readframes(1000000) # 1 million frames max
    #     print("Params: {}".format(params))
    #     # print("Frames: {}".format(frames))

    # # print(params)