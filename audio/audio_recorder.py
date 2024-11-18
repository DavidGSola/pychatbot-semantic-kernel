import os
import threading
import pyaudio
import wave
from typing import ClassVar

class AudioRecorder:
    FORMAT: ClassVar[int] = pyaudio.paInt16
    CHANNELS: ClassVar[int] = 1
    RATE: ClassVar[int] = 44100
    CHUNK: ClassVar[int] = 1024

    is_recording: bool = False
    output_filepath: str

    def record_audio(self):
        self.output_filepath = os.path.join(os.path.dirname(__file__), "output.wav")

        self.is_recording = True
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        frames = []

        while self.is_recording:
            data = stream.read(self.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        with wave.open(self.output_filepath, "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b"".join(frames))

        audio.terminate()

    def start_recording(self):
        if not self.is_recording:  
            self.is_recording = True  
            self.audio_thread = threading.Thread(target=self.record_audio)  
            self.audio_thread.start()  

    def stop_recording(self):  
        if self.is_recording:  
            self.is_recording = False  
            if self.audio_thread is not None:  
                self.audio_thread.join()

    def remove_output_file(self) -> None:
        os.remove(self.output_filepath)