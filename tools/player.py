import vlc


class Player:
    def __init__(self, path: str):
        self.path = path
        self.speaker = vlc.MediaPlayer(path)

    def play(self):
        self.speaker.play()

    def stop(self):
        self.speaker.pause()

    def change_voice(self, path):
        self.speaker = vlc.MediaPlayer(path)