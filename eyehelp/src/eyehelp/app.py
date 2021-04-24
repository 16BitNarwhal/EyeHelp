"""
Reduce eye strain on screens
"""
# import packages
import toga 
from toga.style.pack import Pack, COLUMN
import threading
import time

class EyeHelp(toga.App):
    # Called when application starts
    def startup(self):
        # Constants
        self.CHECKUP_TIME = 3 # 20 * 60 # 3 seconds for testing

        main_box = toga.Box(style=Pack(direction=COLUMN))
        
        # Create and buttons to main box content
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

        # Create and show main window
        self.main_window = toga.MainWindow(title=self.formal_name)         
        self.main_window.content = main_box
        self.main_window.show()

    # Starts a thread so application can work while timer runs
    def begin_timer(self, widget):
        print('Timer started')
        self.do_time = True
        self.timer_thread = threading.Thread(target=self.timer_thread)
        self.timer_thread.start()

    # will be used to break out of thread loop
    def stop_timer(self, widget):
        self.do_time = False
    
    # timer that will notify user after some time (forever)
    def timer_thread(self):
        while True:
            time.sleep(self.CHECKUP_TIME)
            print('Checkup time')

            # Stop timer thread
            if not self.do_time:
                print('Timer stopped')
                break
            
            # calls the notify function
            command = toga.Command(self.notify, 'Command')
            command.action(command)

    # may replace with a python windows balloon tip notifier vvv
    # notifies the user with a dialog box
    def notify(self, widget):
        print('Eye notification')
        self.main_window.info_dialog(
            'Eye Help',
            'It has been 20 minutes, please take a 20 seconds break'
        )


def main():
    return EyeHelp()
