import speech_recognition as sr
import wave
import pyaudio
import threading

class SpeechModule:
    def __init__(self, filename="recordedAudio.wav"):
        self.recognizer = sr.Recognizer()
        self.filename = filename
        self.recording = False
        self._record_thread = None

    def start_recording(self):
        """Start recording audio in a background thread."""
        if self.recording:
            return  # Already recording
        self.recording = True
        self._record_thread = threading.Thread(target=self._record_audio, daemon=True)
        self._record_thread.start()

    def stop_recording(self):
        """Stop the recording."""
        self.recording = False
        if self._record_thread is not None:
            self._record_thread.join()
            self._record_thread = None

    def _record_audio(self):
        RATE, CHUNK, FORMAT, CHANNELS = 16000, 1024, pyaudio.paInt16, 1
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
        )
        frames = []

        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
        print(f"Audio recorded and saved to {self.filename}")

    def recognize_audio(self):
        """Transcribe the saved WAV file using Google Speech Recognition."""
        try:
            with sr.AudioFile(self.filename) as source:
                print("Processing audio...")
                audio_data = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
