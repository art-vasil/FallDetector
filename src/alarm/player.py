import os
import pyttsx3

from settings import ALARM_TEXT, ALARM_DIR


class AlarmPlayer:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 125)
        self.engine.setProperty('volume', 5.0)

    def play(self):
        alarm_file_path = os.path.join(ALARM_DIR, 'alarm.wav')
        self.engine.save_to_file(ALARM_TEXT, alarm_file_path)
        self.engine.runAndWait()

        return alarm_file_path


if __name__ == '__main__':
    AlarmPlayer().play()
