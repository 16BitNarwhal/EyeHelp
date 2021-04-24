'''
Reduce eye strain on screens
'''
# import packages
import toga 
from toga.style.pack import Pack, COLUMN, ROW
import threading
import time
import os
import sys
import eyehelp.face_detect as fd

class EyeHelp(toga.App):
    # Called when application starts
    def startup(self):
        # Images
        path = os.path.dirname(sys.argv[0])

        # Constants
        self.CHECKUP_TIME = 10 # 20 * 60 
        self.BREAK_TIME = 3 # 20 

        # Activity box
        activity_box = toga.Box(style=Pack(direction=COLUMN, background_color='aqua'))

        self.timer_running = False

        self.start_button = toga.Button(
            'Start Timer!',
            on_press=self.begin_timer,
            style=Pack(padding_left=50, padding_right=50, padding_top=20, 
                background_color='violet', height=30)
        )

        self.stop_button = toga.Button(
            'Stop Timer!',
            on_press=self.stop_timer,
            style=Pack(padding_left=50, padding_right=50, padding_top=10, padding_bottom=20, 
                background_color='violet', height=30),
            enabled=False
        )

        activity_box.add(self.start_button)
        activity_box.add(self.stop_button)

        # Config box
        config_box = toga.Box(style=Pack(direction=COLUMN, background_color='aqua'))
        self.video_switch = toga.Switch(
            'Show Video',
            style=Pack(padding_left=50, padding_right=50, padding_top=20, padding_bottom=20,
                background_color='red')
        )

        config_box.add(self.video_switch)

        options = toga.OptionContainer(style=Pack(direction=ROW, background_color='snow'))
        options.add('Activity', activity_box)
        options.add('Configuration', config_box)

        main_box = toga.Box(style=Pack(padding=(10,10), direction=COLUMN, height=400, background_color='snow'))
        main_box.add(options)

        # Create and show main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(400,400), resizeable=False)
        self.main_window.content = main_box
        self.main_window.show()

    # Starts a thread so application can work while timer runs
    def begin_timer(self, widget):
        if self.timer_running:
            print('[App] Timer already running')
            return
        print('[App] Timer started') 
        # toggle buttons usage
        self.start_button.enabled = False
        self.stop_button.enabled = True

        self.timer_running = True
        fd.detect_exit = False
        
        # start threads
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
        # toggle buttons usage
        self.start_button.enabled = True
        self.stop_button.enabled = False

        fd.detect_exit = True

        # join threads
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

                # restart timer and blink counter
                start_time = time.time()
                fd.blink_count = 0

            # When user has left screen for more than some time (BREAK_TIME)
            if not fd.has_face:
                start_time = time.time()

            # exit loop / stop timer
            if fd.detect_exit:
                self.timer_running = False
                break
            
        # make sure button usage is changed (if opencv is force quitted with q key)
        self.start_button.enabled = True
        self.stop_button.enabled = False
        
    # starts face detection in face_detect.py
    def start_detect(self):
        fd.start_detection(self.BREAK_TIME, self.video_switch.is_on)

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
