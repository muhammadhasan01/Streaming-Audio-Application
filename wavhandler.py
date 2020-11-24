import wave
import sys
import pyaudio  

class WavHandler():
    def __init__(self, fpath):
        self.file = wave.open(fpath,"rb")
        self.metadata = self.get_metadata_audio()
        self.chucks = self.get_chunks_audio()

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

        #sample width
        sample_width = file.getsampwidth()
        #num channel
        num_channels = file.getnchannels()
        #sample rate
        sample_rate = file.getframerate()

        return {"sample_width": sample_width, 
                "num_channels": num_channels, 
                "sample_rate": sample_rate}

    def get_chunks_audio(self):
        return []

if __name__ == "__main__":
    port = sys.argv[1]
    wav_file_path = sys.argv[2]

    print("port: {}".format(port))
    print("wav_file_path: {}".format(wav_file_path))

    wav = WavHandler(wav_file_path)

    metadata = wav.get_metadata_audio()
    print("metadata: {}".format(metadata))

    wav.play_wav_audio()