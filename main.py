import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from tools import player
from tools.functions import current_time, current_date, day_of_the_week, get_description_weather, get_temperature, \
    get_news
import os
import time
from threading import Thread
import multiprocessing
import settings


class Assistant:
    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()

        self.speaker = player.Player(os.path.join(settings.TEMPLATES_DIR, 'hi1.mp3'))

        self.ACTIVATION_PHASES = ['system', 'assistant']
        self.STOP_PHRASES = ['stop', 'shut up', 'shut down']
        self.CONTINUE_PHRASES = ['resume', 'Resume', 'continue', 'Continue', 'go on', 'Go on']

        self.TIME_VARIANTS = ['time is it now', 'time is now', 'what is the time now', 'time is it', 'time it is',
                              'tell me the time', 'do you have the time', 'have you got the time']
        self.DAY_OF_THE_WEEK_VARIANTS = ['day of the week', 'day is it', 'day is it now', 'day is it today']
        self.DATE_VARIANTS = ['what date is it today', 'what date is it', "what's the date"]
        self.WEATHER_TEMPERATURE_VARIANTS = ["what's the temperature in", 'what is the temperature',
                                             'what, in degrees, is it', 'how many degrees', 'you know the temperature']
        self.WEATHER_VARIANTS = ["what's the weather in", "what is the weather like in", "what is the weather in"]
        self.NEWS_VARIANTS = ["what's going on in the world", 'show me the latest news', 'read the news for me',
                              'what do they write about in newspapers', "what's in the newspapers",
                              "what's been in the newspapers", "news"]
        self.TIMER_VARIANTS = ['set timer for', ]
        self.CHANGE_TIMER_VARIANTS = ['change timer time to']
        self.CANCEL_TIMER_VARIANTS = ['remove timer', 'cancel timer', 'delete timer']
        self.ALARM_VARIANTS = ['set alarm for', 'set  alarm at']
        self.NOTIFICATION_ADDING_VARIANTS = ['new notification', 'add new notification', 'notification',
                                             'add new reminder']
        self.MUSIC_PLAY_VARIANTS = ['play ']
        self.EBAY_SEARCHING_VARIANTS = ['ebay']
        self.NEXT_PRODUCT_VARIANTS = ['next', 'move to the next one', 'move on']
        self.PREV_PRODUCT_VARIANTS = ['go back', 'read the last one', 'read the previous one']
        self.EXIT_EBAY_VARIANTS = ['exit from ebay']
        self.DESCRIPTION_VARIANTS = ['description', 'read the description']
        self.ADDING_TO_BASKET_VARIANTS = ['add to basket']
        self.SHOW_BASKET_VARIANTS = ['show my shopping cart', 'my shopping cart', 'show my basket']

        self.CURRENT_STATE = 'IDLE'
        self.PREVIOUS_STATE = ''

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

                    if (self.contains(statement, self.STOP_PHRASES)):  # Продолжить речь
                        if (self.CURRENT_STATE == 'SPEAKING'):
                            self.speaker.stop()
                            self.PREVIOUS_STATE = 'SPEAKING'
                            self.CURRENT_STATE = 'IDLE'
                            print('Cменилось состояние с SPEAKING на IDLE')
                        if (self.CURRENT_STATE == 'PLAYING_NEWS'):
                            self.speaker.stop()
                            self.PREVIOUS_STATE = 'PLAYING_NEWS'
                            self.CURRENT_STATE = 'IDLE'
                            print('Cменилось состояние с PLAYING_NEWS на IDLE')

                    if (self.contains(statement, self.CONTINUE_PHRASES)):
                        if (self.PREVIOUS_STATE == 'SPEAKING'):
                            self.speaker.play()
                            self.CURRENT_STATE = 'SPEAKING'
                            self.PREVIOUS_STATE = 'IDLE'
                            print('Cменилось состояние с IDLE на SPEAKING')
                        if (self.PREVIOUS_STATE == 'PLAYING_NEWS'):
                            self.speaker.play()
                            self.CURRENT_STATE = 'PLAYING_NEWS'
                            self.PREVIOUS_STATE = 'IDLE'
                            print('Cменилось состояние с IDLE на PLAYING_NEWS')

                    if (self.CURRENT_STATE == 'IDLE'):
                        if (self.contains(statement, self.TIME_VARIANTS)):
                            self.say(text=current_time(), previous_state='IDLE')
                            break
                        if (self.contains(statement, self.DAY_OF_THE_WEEK_VARIANTS)):
                            self.say(text=day_of_the_week(), previous_state='IDLE')
                            break
                        if (self.contains(statement, self.DATE_VARIANTS)):
                            self.say(text=current_date(), previous_state='IDLE')
                            break
                        if (self.contains(statement, self.WEATHER_TEMPERATURE_VARIANTS)):
                            city = self.get_city_name(statement, self.WEATHER_TEMPERATURE_VARIANTS)
                            self.say(text=get_temperature(city), previous_state='IDLE')
                            break
                        if (self.contains(statement, self.NEWS_VARIANTS)):
                            news, urls = get_news()
                            news = "".join(news[:10])
                            self.say(text=news, previous_state='IDLE', speaker='News')
                            break
                        if (self.contains(statement, self.TIMER_VARIANTS)):
                            for item in self.TIMER_VARIANTS:
                                if (item in statement):
                                    statement = statement.replace(item, "")

                            if ('minute' in statement):
                                statement = statement.replace('minutes', "")
                                statement = statement.replace('minute', "")
                                delay = int(statement) * 60

                            if ('second' in statement):
                                statement = statement.replace('seconds', "")
                                statement = statement.replace('second', "")
                                delay = int(statement)

                            if ('hour' in statement):
                                statement = statement.replace('hours', "")
                                statement = statement.replace('hour', "")
                                delay = int(statement) * 3600

                            print(f'Таймер на {delay} секунд')

                            self.timer_thread = multiprocessing.Process(target=self.timer, args=[delay])
                            self.timer_thread.start()

                            self.say(text='Started timer', previous_state='IDLE')
                            break

                    if (self.contains(statement, self.CANCEL_TIMER_VARIANTS)):
                        self.timer_thread.terminate()
                        print('поток вроде сдох')
                        break

                    break
                except sr.UnknownValueError:  # Не смог распознать
                    pass
                    break
                except sr.RequestError as e:
                    print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
                    break
        except KeyboardInterrupt:
            print("Пока!")
            exit()

    def say(self, text, speaker='None', previous_state='IDLE'):
        # TODO спикер работает в отдельном потоке так что можно будет сделать стоппинг как в оригинале
        if (speaker == 'None'):
            print(f'Запрос на синтез речи: {text}')
            tts = gTTS(text)

            directory = settings.TEMP_VOICE_DIR
            filename = f'temp{len(os.listdir(directory)) + 1}.mp3'
            tts.save(os.path.join(directory, filename))
            print('Успешно синтезирована речь')

            self.PREVIOUS_STATE = previous_state
            self.CURRENT_STATE = 'SPEAKING'

            self.speaker.change_voice(os.path.join(directory, filename))
            played = self.speaker.play()  # Нужно для того чтобы отметить когда закончилось воспроизведение
            thread = Thread(target=self.change_state, args=[self.PREVIOUS_STATE, played])
            thread.start()
            print(thread.ident)

        elif (speaker == 'News'):
            print(f'Запрос на синтез речи: {text}')
            tts = gTTS(text)

            directory = settings.TEMP_VOICE_DIR
            filename = f'temp{len(os.listdir(directory)) + 1}.mp3'
            tts.save(os.path.join(directory, filename))
            print('Успешно синтезирована речь')

            self.PREVIOUS_STATE = previous_state
            self.CURRENT_STATE = 'PLAYING_NEWS'

            self.speaker.change_voice(os.path.join(directory, filename))
            played = self.speaker.play()  # Нужно для того чтобы отметить когда закончилось воспроизведение
            thread = Thread(target=self.change_state, args=[self.PREVIOUS_STATE, played])
            thread.start()

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

    def get_city_name(self, city, variants):
        for el in variants:
            if (el in city):
                city = city.replace(el, "")
        return city

    def change_state(self, prev, delay):
        """
        Функция которая меняет состояние бота после синтеза речи
        :param prev: Состояние, которое будет поставлено
        :param delay: Таймер, после которго будет изменено состояние (в миллисекундах)
        :return: none
        """
        time.sleep(delay)
        self.CURRENT_STATE = prev
        print('Состояние сменилось на ', prev)

    def timer(self, delay):
        print(f'Начат таймер на {delay} секунд')
        time.sleep(delay)
        os.popen(f"ffplay -nodisp -autoexit {os.path.join(settings.TEMPLATES_DIR, 'alarm.mp3')}")
        print('таймер закончен')


helper = Assistant()

while True:
    helper.work()
