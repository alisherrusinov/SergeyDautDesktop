import vlc
import time
import threading


class Player:
    def __init__(self, path: str):
        self.path = path
        self.speaker = vlc.MediaPlayer(path)

    def play(self):
        played = False
        self.speaker.play()
        time.sleep(1.5)
        return self.speaker.get_length()/1000

    def play_news(self):
        self.speaker.play()

    def stop(self):
        self.speaker.pause()

    def change_voice(self, path):
        self.speaker = vlc.MediaPlayer(path)

    def get_len(self):
        return self.speaker.get_duration()

