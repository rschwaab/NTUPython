import speech_recognition as sr

class SpeechModule:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen_and_recognize(self):
        with self.microphone as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        
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