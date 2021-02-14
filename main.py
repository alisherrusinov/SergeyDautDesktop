import speech_recognition as sr
import requests, bs4
import os
import sys
import time
import datetime
import logging
import webbrowser
import subprocess
import random



class FRIDAY:
    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()
        # file = open("dict.txt","r",encoding="utf8")
        # self.dict = {}
        # kor = []
        # for st in file:
        #     kor.append(st)
        #     if st[-2] ==".":
        #         kor = str(kor)
        #         kor = kor.replace("['","")
        #         kor = kor.replace("\\n","")
        #         kor = kor.split("@")
        #         self.dict[kor[0].lower()] = kor[1]
        #     kor = []
        # file.close()

        # file.close()
        self.nowpath = os.getcwd()
        self.balabpath = self.nowpath + "/yalcon/yalcon.exe"
        file = open("phrases.txt", "r", encoding='utf8')
        self.phrases = {}
        for i in file:
            i = i.split("@")
            newi = []
            newi = i[1].split("#")
            for j in range(len(newi)):
                el = newi[j]
                el = el.lower()
                el = el.replace("\n", "")
                newi[j] = el
            self.phrases[i[0]] = newi
        file.close()
        self.phraskeys = self.phrases.keys()
        # self.dictkeys = self.dict.keys()

        # self.com = serial.Serial(self.smartHouse["port"],9600)

    def work(self):
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)
        try:
            while True:
                with self._microphone as source:
                    audio = self._recognizer.listen(source, phrase_time_limit=2)
                try:
                    statement = self._recognizer.recognize_google(audio, language="ru_RU")
                    statement = statement.lower()
                    print(statement)
                    if statement in self.phrases["приветствия"]:
                        ans = random.choice(self.phrases["приветствия"])
                        self.say(ans)
                        break
                    if statement in self.phrases["как дела_input"]:
                        ans = random.choice(self.phrases["как дела_output"])
                        self.say(ans)
                        time.sleep(0.1)
                        self.say("а у вас?")
                        break
                    if statement in self.phrases["как дела_output"]:
                        ans = random.choice(self.phrases["как дела_ans"])
                        self.say(ans)
                        break
                    if statement in self.phrases["спасибо_input"]:
                        ans = random.choice(self.phrases["спасибо_output"])
                        self.say(ans)
                        break
                    break
                except sr.UnknownValueError:
                    pass
                    break
                except sr.RequestError as e:
                    print("Не могу получить данные от сервиса Google Speech Recognition; {0}".format(e))
                    break
        except KeyboardInterrupt:
            print("Пока!")

    def say(self, phrase):
        print('ответ:',phrase)


while True:
    FRIDAY().work()