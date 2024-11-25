import speech_recognition as sr

class SpeechModule:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen_and_recognize(self):
        print("Listening... Press Enter to stop.")
        audio_data = []

        def callback(recognizer, audio):
            audio_data.append(audio)

        stop_listening = self.recognizer.listen_in_background(self.microphone, callback)

        input()  # Wait for the user to press Enter
        stop_listening(wait_for_stop=False)

        if not audio_data:
            return "No audio data captured"

        audio = sr.AudioData(b''.join([a.get_raw_data() for a in audio_data]), audio_data[0].sample_rate, audio_data[0].sample_width)

        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

# Example usage from another class
class ExampleUsage:
    def __init__(self):
        self.speech_module = SpeechModule()

    def get_speech_input(self):
        return self.speech_module.listen_and_recognize()

if __name__ == "__main__":
    example = ExampleUsage()
    print(example.get_speech_input())