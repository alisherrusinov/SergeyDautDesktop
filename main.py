import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from tools import player
import os
import settings


class Assistant:
    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()

        self.speaker = player.Player(os.path.join(settings.TEMPLATES_DIR, 'hi1.mp3'))

    def work(self):
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)
        try:
            while True:
                with self._microphone as source:
                    audio = self._recognizer.listen(source)
                try:
                    statement = self._recognizer.recognize_google(audio, language="en_en")
                    statement = statement.lower()
                    print(statement)
                    self.speaker.play()
                    break
                except sr.UnknownValueError:  # Не смог распознать
                    pass
                    break
                except sr.RequestError as e:
                    print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
                    break
        except KeyboardInterrupt:
            print("Пока!")

    def say(self, text):
        print(text)
        tts = gTTS(text)

        directory = settings.TEMP_VOICE_DIR
        filename = f'temp{len(os.listdir(directory)) + 1}.mp3'
        tts.save(filename)
        print('Успешно синтезирована речь')


helper = Assistant()

while True:
    helper.work()
