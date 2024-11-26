import speech_recognition as sr
import wave
import pyaudio
import threading

class SpeechModule:
    def __init__(self, filename="recordedAudio.wav"):
        self.recognizer = sr.Recognizer()
        self.filename = filename  # File to save the recorded audio
        self.recording = True

    def listen_and_recognize(self):
        """Records audio until Enter is pressed and transcribes it."""
        self.record_audio()  # Record audio
        return self.recognize_audio()  # Transcribe the recorded audio

    def record_audio(self):
        """Records audio from the microphone and saves it as a WAV file."""
        RATE, CHUNK, FORMAT, CHANNELS = 16000, 1024, pyaudio.paInt16, 1
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
        )
        frames = []

        def stop_recording():
            input("Press Enter to stop recording...")
            self.recording = False

        threading.Thread(target=stop_recording, daemon=True).start() # Needed to in order to wait for user to press enter.

        while self.recording:
            frames.append(stream.read(CHUNK))

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
        """Transcribes the saved WAV file using Google Speech Recognition."""
        try:
            with sr.AudioFile(self.filename) as source:
                print("Processing audio...")
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"


# Example usage
if __name__ == "__main__":
    speech_module = SpeechModule()
    print(speech_module.listen_and_recognize())