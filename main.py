import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from tools import player
from tools.functions import current_time, current_date, day_of_the_week, get_description_weather
import os
import settings


class Assistant:
    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()

        self.speaker = player.Player(os.path.join(settings.TEMPLATES_DIR, 'hi1.mp3'))

        self.ACTIVATION_PHASES = ['system', 'assistant']

        self.TIME_VARIANTS = ['time is it now', 'time is now', 'what is the time now', 'time is it', 'time it is',
                              'tell me the time', 'do you have the time', 'have you got the time']
        self.DAY_OF_THE_WEEK_VARIANTS = ['day of the week', 'day is it', 'day is it now', 'day is it today']
        self.DATE_VARIANTS = ['what date is it today', 'what date is it', "what's the date"]
        self.WEATHER_TEMPERATURE_VARIANTS = ["what's the temperature in", 'what is the temperature', 'what, in degrees, is it', 'how many degrees', 'you know the temperature']
        self.WEATHER_VARIANTS = ["what's the weather in", "what is the weather like in", "what is the weather in"]
        self.NEWS_VARIANTS = ["what's going on in the world", 'show me the latest news', 'read the news for me', 'what do they write about in newspapers', "what's in the newspapers", "what's been in the newspapers", "news"]
        self.TIMER_VARIANTS = ['set timer for',]
        self.CHANGE_TIMER_VARIANTS = ['change timer time to']
        self.CANCEL_TIMER_VARIANTS = ['remove timer', 'cancel timer', 'delete timer']
        self.ALARM_VARIANTS = ['set alarm for', 'set  alarm at']
        self.NOTIFICATION_ADDING_VARIANTS = ['new notification', 'add new notification', 'notification', 'add new reminder']
        self.MUSIC_PLAY_VARIANTS = ['play ']
        self.EBAY_SEARCHING_VARIANTS = ['ebay']
        self.NEXT_PRODUCT_VARIANTS = ['next', 'move to the next one', 'move on']
        self.PREV_PRODUCT_VARIANTS = ['go back', 'read the last one', 'read the previous one']
        self.EXIT_EBAY_VARIANTS = ['exit from ebay']
        self.DESCRIPTION_VARIANTS = ['description', 'read the description']
        self.ADDING_TO_BASKET_VARIANTS = ['add to basket']
        self.SHOW_BASKET_VARIANTS = ['show my shopping cart', 'my shopping cart', 'show my basket']

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
                    if(self.contains(statement, self.TIME_VARIANTS)):
                        self.say(current_time())
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
        #TODO спикер работает в отдельном потоке так что можно будет сделать стоппинг как в оригинале
        print(f'Запрос на синтез речи: {text}')
        tts = gTTS(text)

        directory = settings.TEMP_VOICE_DIR
        filename = f'temp{len(os.listdir(directory)) + 1}.mp3'
        tts.save(os.path.join(directory, filename))
        print('Успешно синтезирована речь')

        self.speaker.change_voice(os.path.join(directory, filename))
        self.speaker.play()

    def contains(self, text, variants):
        """
        Функция которая проверяет наличие элемента в списке
        :param text: Текст который сверять нужно
        :param variants: Список вариантов
        :return: true если есть совпадение в списке вариантов
        """
        status = False
        for el in variants:
            if (el in text):
                status = True

        return status


helper = Assistant()

while True:
    helper.work()
