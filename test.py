from scipy.io.wavfile import read
from pydub import AudioSegment

rate, signal = read("./sample_wav/test1.wav")
channel1 = signal[:,0]

audio_segment = pydub.AudioSegment(
    channel1.tobytes(), 
    frame_rate=rate,
    sample_width=channel1.dtype.itemsize, 
    channels=1
)

# test that it sounds right (requires ffplay, or pyaudio):
from pydub.playback import play
loop = AudioSegment.from_wav("metallic-drums.wav")

play(loop)