import wave
import sys
import pyaudio  

from pydub import AudioSegment
from pydub.utils import make_chunks

CHUNK_SIZE = 32767 # In bytes.

class WavHandler():
    def __init__(self, fpath):
        # self.file = wave.open(fpath,"rb")
        self.file = AudioSegment.from_file(file=fpath, format="wav")

        self.metadata = self.get_metadata_audio()
        self.chunks = self.get_chunks_audio()
        self.max_chunk_size = 1024

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
        file = self.file

        # sample width
        sample_width = file.sample_width
        # num channel
        num_channels = file.channels
        # sample rate
        sample_rate = file.frame_rate

        return {"sample_width": sample_width, 
                "num_channels": num_channels, 
                "sample_rate": sample_rate}

    def get_chunks_audio(self):
        nChannels = self.metadata["num_channels"]
        sampleWidth = self.metadata["sample_width"]
        frameRate = self.metadata["sample_rate"]

        frameSize = nChannels * sampleWidth # In bytes
        frameCountPerChunk = CHUNK_SIZE / frameSize

        chunkTime = 1000 * frameCountPerChunk / frameRate # In milliseconds.

        chunks = make_chunks(self.file, chunkTime) #Make chunks of one sec
        print("Length of Chunks: {}".format(len(chunks)))
        print("Chunks: {}".format(chunks))
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

    from scipy.io.wavfile import read
    from pydub import AudioSegment

    rate, signal = read(wav_file_path)
    channel1 = signal[:]

    audio_segment = AudioSegment(
        channel1.tobytes(), 
        frame_rate=rate,
        sample_width=channel1.dtype.itemsize, 
        channels=1
    )

    # test that it sounds right (requires ffplay, or pyaudio):
    from pydub.playback import play
    play(audio_segment)

    with wave.open(wav_file_path) as fd:
        params = fd.getparams()
        frames = fd.readframes(1000000) # 1 million frames max
        print("Params: {}".format(params))
        # print("Frames: {}".format(frames))

    # print(params)