"""
Reduce eye strain on screens
"""
import toga 
from toga.style.pack import Pack, COLUMN
import threading
import time

class EyeHelp(toga.App): 

    def startup(self):
        # Constants
        self.CHECKUP_TIME = 3 # 20 * 60 # 3 seconds for testing

        main_box = toga.Box(style=Pack(direction=COLUMN))

        start_button = toga.Button(
            'Start Timer!',
            on_press=self.begin_timer,
            style=Pack(padding=(10, 100), height=30)
        )

        stop_button = toga.Button(
            'Stop Timer!',
            on_press=self.stop_timer,
            style=Pack(padding=(10, 100), height=30)
        )

        main_box.add(start_button)
        main_box.add(stop_button)

        self.main_window = toga.MainWindow(title=self.formal_name)         
        self.main_window.content = main_box
        self.main_window.show()

    def begin_timer(self, widget):
        print('Timer started')
        self.do_time = True
        self.timer_thread = threading.Thread(target=self.timer_thread)
        self.timer_thread.start() 

    def stop_timer(self, widget):
        self.do_time = False
    
    def timer_thread(self):
        while True:
            time.sleep(self.CHECKUP_TIME)
            print('Checkup time')
            if not self.do_time:
                print('Timer stopped')
                break

            command = toga.Command(self.notify, 'Command')
            command.action(command)

    # may replace with a python windows balloon tip notifier
    def notify(self, widget):
        print('Eye notification')
        self.main_window.info_dialog(
            'Eye Help',
            'It has been 20 minutes, please take a 20 seconds break'
        )


def main():
    return EyeHelp()
