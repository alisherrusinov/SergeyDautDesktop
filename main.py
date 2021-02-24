import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from tools import player
from tools.functions import current_time, current_date, day_of_the_week, get_description_weather, get_temperature, \
    get_news, get_youtube_music, get_seconds_from_date, search_ebay, get_description_ebay
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

        self.ACTIVATION_PHASES = ['system', 'assistant', 'assistance', 'my sister', 'my system', 'sister']
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
        self.TIMER_VARIANTS = ['set timer for', 'set alarm for']
        self.CHANGE_TIMER_VARIANTS = ['change timer time to']
        self.CANCEL_TIMER_VARIANTS = ['remove timer', 'cancel timer', 'delete timer']
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
        self.CLEAR_BASKET_VARIANTS = ['clear my basket', 'clear my shopping cart']

        self.CURRENT_STATE = 'IDLE'
        self.PREVIOUS_STATE = ''

        self.SHOPPING_CART, self.shopping_cart_names = self.read_shopping_cart()

        self.change_state_thread = None

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

                    if (self.contains(statement, self.STOP_PHRASES)):  # Прекратить речь
                        if (self.CURRENT_STATE == 'SPEAKING'):
                            self.speaker.stop()
                            self.CURRENT_STATE = self.PREVIOUS_STATE
                            self.PREVIOUS_STATE = 'SPEAKING'
                            print(f'Cменилось состояние с SPEAKING на {self.CURRENT_STATE}')
                    if (self.contains(statement, self.CONTINUE_PHRASES)):
                        if (self.PREVIOUS_STATE == 'SPEAKING'):
                            self.speaker.play()
                            # TODO: СДЕЛАТЬ ЗАПУСК ТАЙМЕРА НО С ДЕЛЬТОЙ(В ФАЙЛЕ КАКОМ-ТО БЫЛО ЭТО)
                            self.PREVIOUS_STATE = self.CURRENT_STATE
                            self.CURRENT_STATE = 'SPEAKING'
                            print(f'Cменилось состояние с IDLE на SPEAKING')

                    if (self.contains(statement, self.NEXT_PRODUCT_VARIANTS)):
                        if (self.CURRENT_STATE == 'SEARCHING_PRODUCTS'):
                            self.current_product += 1
                            self.say(text=self.products[self.current_product], previous_state='SEARCHING_PRODUCTS')
                    if (self.contains(statement, self.PREV_PRODUCT_VARIANTS)):
                        if (self.CURRENT_STATE == 'SEARCHING_PRODUCTS'):
                            if (self.current_product == 0):
                                self.say(text='it is the first product', previous_state='SEARCHING_PRODUCTS')
                            else:
                                self.current_product -= 1
                                self.say(text=self.products[self.current_product], previous_state='SEARCHING_PRODUCTS')


                    if (self.CURRENT_STATE == 'ADDING_NOTIFICATION'): # Вот это и следующее условие нужно поместить вне активационной фразы т.к. предполагается что просто фраза идет
                        self.notification_label = statement
                        self.say(text='tell me when should i remind', previous_state='ADDING_DATE_NOTIFICATION')
                        self.CURRENT_STATE = 'ADDING_DATE_NOTIFICATION'
                        continue
                    if (self.CURRENT_STATE == 'ADDING_DATE_NOTIFICATION'):
                        delta = get_seconds_from_date(statement)
                        if (not delta):
                            self.say("I didn't recognised date. Please repeat",
                                     previous_state='ADDING_DATE_NOTIFICATION')
                            break
                        print(delta)
                        print(self.notification_label)

                        print(f'Запрос на синтез речи: {self.notification_label}')
                        tts = gTTS(self.notification_label)
                        directory = settings.TEMP_VOICE_DIR
                        filename = f'temp{len(os.listdir(directory)) + 1}.mp3'
                        filename = os.path.join(directory, filename)
                        tts.save(filename)
                        print('Успешно синтезирована речь')

                        self.reminder_thread = multiprocessing.Process(target=self.timer, args=[delta, filename])
                        self.reminder_thread.start()
                        self.CURRENT_STATE = 'IDLE'
                        continue


                    if (True):# Раньше тут были активационные фразы но я не буду убирать этот иф т.к. с ним код раздельнее
                        statement = statement.replace('assistant', '')
                        statement = statement.replace('a system', '')
                        statement = statement.replace('system', '')

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
                            if (self.contains(statement, self.WEATHER_VARIANTS)):
                                city = self.get_city_name(statement, self.WEATHER_VARIANTS)
                                self.say(text=get_description_weather(city), previous_state='IDLE')
                                break
                            if (self.contains(statement, self.NEWS_VARIANTS)):
                                news, urls = get_news()
                                news = "".join(news[:5])
                                self.say(text=news, previous_state='IDLE')
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
                            if (self.contains(statement, self.CHANGE_TIMER_VARIANTS)):
                                for item in self.CHANGE_TIMER_VARIANTS:
                                    if (item in statement):
                                        statement = statement.replace(item, "")
                                statement = statement.replace('-', '')

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

                                print(f'Изменен таймер на {delay} секунд')

                                self.timer_thread.kill()
                                self.timer_thread = multiprocessing.Process(target=self.timer, args=[delay])
                                self.timer_thread.start()

                                self.say(text='Started timer', previous_state='IDLE')
                                break

                            if (self.contains(statement, self.CANCEL_TIMER_VARIANTS)):
                                self.timer_thread.kill()
                                print('Завершен таймер')
                                self.say('Cancelled timer', previous_state='IDLE')
                                break

                            if (self.contains(statement, self.MUSIC_PLAY_VARIANTS)):
                                statement = statement.replace('play ', "")
                                song = get_youtube_music(statement)
                                print(song)
                                self.speaker.change_voice(song, youtube=True)
                                self.speaker.play()
                                self.CURRENT_STATE = 'SPEAKING'
                                self.PREVIOUS_STATE = 'IDLE'
                                played = self.speaker.play_youtube()  # Нужно для того чтобы отметить когда закончилось воспроизведение
                                print(played)

                                self.change_state_thread = Thread(target=self.change_state,
                                                                  args=[self.PREVIOUS_STATE, self.CURRENT_STATE, played])
                                self.change_state_thread.start()
                                break

                            if (self.contains(statement, self.NOTIFICATION_ADDING_VARIANTS)):
                                self.say(text='tell me what should I remind', previous_state='ADDING_NOTIFICATION')
                                self.CURRENT_STATE = 'ADDING_NOTIFICATION'
                                continue
                            if (self.contains(statement, self.EXIT_EBAY_VARIANTS)):
                                self.say("I'm not on ebay")
                                break
                            if (self.contains(statement, self.SHOW_BASKET_VARIANTS)):
                                self.write_basket()
                                answer = ""
                                for el in self.shopping_cart_names:
                                    answer += f"{el}. "
                                self.say(answer, previous_state='IDLE')
                                break
                            if (self.contains(statement, self.CLEAR_BASKET_VARIANTS)):
                                self.clear_basket()
                                self.say('Cleared the basket', previous_state='IDLE')
                                break
                            if (self.contains(statement, self.EBAY_SEARCHING_VARIANTS)):
                                statement = statement.replace('find me', '')
                                statement = statement.replace('on ebay', '')
                                statement = statement.replace('ebay', '')
                                print(statement)

                                self.products, self.products_urls, self.products_prices = search_ebay(statement)
                                self.current_product = 0

                                self.CURRENT_STATE = 'SEARCHING_PRODUCTS'
                                self.PREVIOUS_STATE = 'IDLE'
                                self.say(text=self.products[self.current_product], previous_state='SEARCHING_PRODUCTS')
                                break


                        elif (self.CURRENT_STATE == 'SEARCHING_PRODUCTS'):
                            if (self.contains(statement, self.EXIT_EBAY_VARIANTS)):
                                self.CURRENT_STATE = 'IDLE'
                                self.say('ok', previous_state='IDLE')
                                break
                            if (self.contains(statement, self.DESCRIPTION_VARIANTS)):
                                decsription = get_description_ebay(self.products_urls[self.current_product])
                                self.say(decsription, previous_state='SEARCHING_PRODUCTS')
                                break
                            if (self.contains(statement, self.ADDING_TO_BASKET_VARIANTS)):
                                self.SHOPPING_CART.append(self.products_urls[self.current_product])
                                self.shopping_cart_names.append(self.products[self.current_product])
                                self.say('Added', previous_state='SEARCHING_PRODUCTS')
                                break
                            if (self.contains(statement, self.SHOW_BASKET_VARIANTS)):
                                self.write_basket()
                                answer = ""
                                for el in self.shopping_cart_names:
                                    answer += f"{el}. "
                                self.say(answer, previous_state='SEARCHING_PRODUCTS')
                                break

                    break
                except sr.UnknownValueError:  # Не смог распознать
                    pass
                    break
                except sr.RequestError as e:
                    print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
                    break
                except Exception as e:
                    print(str(e))
                    self.say('There is some trouble in my work. Can you repeat?')
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

            self.change_state_thread = Thread(target=self.change_state,
                                                               args=[self.PREVIOUS_STATE,self.CURRENT_STATE, played, os.path.join(directory, filename)])
            self.change_state_thread.start()

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

    def change_state(self, change_to, change_from, delay, filename=None):
        """
        Функция которая меняет состояние бота после синтеза речи
        :param prev: Состояние, которое будет поставлено
        :param delay: Таймер, после которго будет изменено состояние (в миллисекундах)
        :return: none
        """
        for i in range(int(delay)):
            if(self.CURRENT_STATE == change_to):
                break
            time.sleep(1)
        self.CURRENT_STATE = change_to
        self.PREVIOUS_STATE = change_from
        print('Состояние сменилось на ', change_to)
        if(filename!=None):
            os.popen(f'rm {filename}')

    def change_state1(self,prev):
        self.CURRENT_STATE = prev

    def timer(self, delay, filename='alarm.mp3'):
        print(f'Начат таймер на {delay} секунд')
        time.sleep(delay)
        if filename == 'alarm.mp3':
            os.popen(f"ffplay -nodisp -autoexit {os.path.join(settings.TEMPLATES_DIR, 'alarm.mp3')}")
        else:
            os.popen(f"ffplay -nodisp -autoexit {filename}")
        print('таймер закончен')

    def write_basket(self):
        file = open('shoppingcart.txt', 'w')
        for product in self.SHOPPING_CART:
            file.write(f'{product}\n')
        file.close()
        file = open('shoppingcartnames.txt', 'w')
        for product in self.shopping_cart_names:
            file.write(f'{product}\n')
        file.close()

    def read_shopping_cart(self):
        file = open('shoppingcart.txt')
        products = file.read().split('\n')
        file.close()
        file = open('shoppingcartnames.txt')
        names = file.read().split('\n')
        file.close()
        return products, names
    def clear_basket(self):
        self.SHOPPING_CART = []
        self.shopping_cart_names = []
        file = open('shoppingcart.txt', 'w')
        file.close()
        file = open('shoppingcartnames.txt', 'w')
        file.close()


helper = Assistant()

while True:
    helper.work()
