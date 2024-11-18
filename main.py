from speechModule import SpeechModule

def main():
    speech_module = SpeechModule()
    result = speech_module.listen_and_recognize()
    print(result)

if __name__ == "__main__":
    main()