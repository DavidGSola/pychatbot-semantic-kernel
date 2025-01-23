import io
import wave
import pyaudio

class AudioPlayer:
    def play_wav_from_bytes(self, wav_bytes, chunk_size=1024):
        p = pyaudio.PyAudio()
        
        try:
            wav_io = io.BytesIO(wav_bytes)
            
            with wave.open(wav_io, 'rb') as wf:
                channels = wf.getnchannels()
                rate = wf.getframerate()
                
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=channels,
                                rate=rate,
                                output=True)
                
                data = wf.readframes(chunk_size)
                while len(data) > 0:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                stream.stop_stream()
                stream.close()
        
        finally:
            p.terminate()