"""
Reduce eye strain on screens
"""
# import packages
import toga 
from toga.style.pack import Pack, COLUMN
import threading
import time
import eyehelp.face_detect as fd
# from eyehelp.face_detect import *

class EyeHelp(toga.App):
    # Called when application starts
    def startup(self):
        # Constants
        self.CHECKUP_TIME = 10 # 20 * 60 
        self.BREAK_TIME = 3 # 20

        main_box = toga.Box(style=Pack(direction=COLUMN))
        
        # Timer buttons
        self.timer_running = False

        start_button = toga.Button(
            'Start Timer!',
            on_press=self.begin_timer,
            style=Pack(padding=(10, 100), height=30)
        )

        stop_button = toga.Button(
            'Stop Timer!',
            on_press=self.stop_timer,
            style=Pack(padding=(5, 100), height=30)
        )

        main_box.add(start_button)
        main_box.add(stop_button)

        # Create and show main window
        self.main_window = toga.MainWindow(title=self.formal_name)         
        self.main_window.content = main_box
        self.main_window.show()

    # Starts a thread so application can work while timer runs
    def begin_timer(self, widget):
        if self.timer_running:
            print('[App] Timer already running')
            return 
        self.timer_running = True
        fd.detect_exit = False
        print('[App] Timer started') 
        self.timer_thread = threading.Thread(target=self.timer_loop)
        self.detect_thread = threading.Thread(target=self.start_detect)
        self.timer_thread.start()
        self.detect_thread.start()

    # will be used to break out of thread loop
    def stop_timer(self, widget): 
        if not self.timer_running:
            print('[App] Timer not start')
            return
    
        print('[App] Timer stopped')
        fd.detect_exit = True
        self.timer_running = False
        self.timer_thread.join()
        self.detect_thread.join()
    
    # timer that will notify user after some time (forever)
    def timer_loop(self):         
        start_time = time.time()
        while True:

            # When user has been on screen for some time (CHECKUP_TIME)
            elapsed_time = time.time() - start_time 
            if elapsed_time >= self.CHECKUP_TIME:
                print('[App] Checkup time')
                
                # calls the notify function
                command = toga.Command(self.notify, 'Command')
                command.action(command)

                # restart time
                start_time = time.time()

            # When user has left screen for more than some time (BREAK_TIME)
            if not fd.has_face:
                start_time = time.time()

            # exit loop / stop timer
            if fd.detect_exit:
                break
        
    # starts face detection in face_detect.py
    def start_detect(self):
        fd.start_detection(self.BREAK_TIME, True)

    # may replace with a python windows balloon tip notifier vvv
    # notifies the user with a dialog box
    def notify(self, widget):
        print('[App] Eye notification')
        self.main_window.info_dialog(
            'Eye Help',
            'It has been 20 minutes, please take a 20 seconds break'
        )

def main():
    return EyeHelp()
