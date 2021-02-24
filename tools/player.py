import vlc
import pafy
import time
import threading


class Player:
    def __init__(self, path: str, youtube=False):
        if(youtube):
            video = pafy.new(path)
            best = video.getbestaudio()
            playurl = best.url
            self.speaker = vlc.MediaPlayer(playurl)
        else:
            self.path = path
            self.speaker = vlc.MediaPlayer(path)

    def play(self):
        played = False
        self.speaker.play()
        time.sleep(0.5)
        return self.speaker.get_length()/1000

    def play_news(self):
        self.speaker.play()

    def play_youtube(self):
        self.speaker.play()
        time.sleep(5)
        return self.speaker.get_length() / 1000

    def stop(self):
        self.speaker.pause()

    def change_voice(self, path, youtube=False):
        if (youtube):
            video = pafy.new(path)
            best = video.getbestaudio()
            playurl = best.url
            del self.speaker
            self.speaker = vlc.MediaPlayer(playurl)
        else:
            self.path = path
            del self.speaker
            self.speaker = vlc.MediaPlayer(path)
