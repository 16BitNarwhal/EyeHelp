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
import random
import eyehelp.face_detect as fd
import eyehelp.calibrate as calibrate

# Label for multiple lines
def MultilineLabel(text : str, box_style : Pack = None, label_style : Pack = None, char_line=30) -> toga.Box :
    children = []
    label_text = ''
    for word in text.split():
        if len(label_text) <= char_line:
            label_text += word + ' '
        else:
            label = toga.Label(label_text, style=label_style)
            children.append(label)
            label_text = word + ' '

    if label_text != '':
        label = toga.Label(label_text, style=label_style)
        children.append(label)
        
    box = toga.Box(id = None, style = box_style,
        children = children)
    return box

class EyeHelp(toga.App):
    # Called when application starts
    def startup(self):
        # Paths and files
        ospath = os.path.dirname(sys.argv[0])
        self.CONFIG_FILE = ospath + '\\config'

        # Constants
        self.CHECKUP_TIME = 10 # 20 * 60 
        self.BREAK_TIME = 3 # 20 

        # Activity box
        activity_box = toga.Box(style=Pack(direction=COLUMN, background_color='aqua'))
        
        self.timer_running = False

        title_label = toga.Label(
            'Eye Help',
            style=Pack(padding_left=50, padding_right=50, padding_top=20,
                font_family='monospace', font_size=30, font_weight='bold')
        )

        instruction = 'Start and stop timer to track your eye blinks and screen usage'
        
        instructions_box = MultilineLabel(
            instruction,
            box_style=Pack(direction=COLUMN, padding_left=50, padding_top=10),
            label_style=Pack(padding_bottom=10, font_family='monospace', font_size=12),
            char_line=35
        )

        self.start_button = toga.Button(
            'Start Timer!',
            on_press=self.begin_timer,
            style=Pack(padding_left=50, padding_right=50, padding_top=20, 
                background_color='violet', height=50, font_family='monospace', font_size=20)
        )

        self.stop_button = toga.Button(
            'Stop Timer!',
            on_press=self.stop_timer,
            style=Pack(padding_left=50, padding_right=50, padding_top=20, padding_bottom=10, 
                background_color='violet', height=50, font_family='monospace', font_size=20),
            enabled=False
        )

        activity_box.add(title_label)
        activity_box.add(self.start_button)
        activity_box.add(self.stop_button)
        activity_box.add(instructions_box)

        # Eye tips box
        # https://www.mayoclinic.org/diseases-conditions/eyestrain/diagnosis-treatment/drc-20372403
        # https://www.health.ny.gov/prevention/tobacco_control/smoking_can_lead_to_vision_loss_or_blindness
        # https://www.health.harvard.edu/blog/will-blue-light-from-electronic-devices-increase-my-risk-of-macular-degeneration-and-blindness-2019040816365
        self.eye_tips = [
            'Try to not to use very bright lighting as the glare can strain your eyes and make the screen harder to look at',
            'Try to put light sources in places that do not directly shine on your eyes',
            'Using non-prescripted eye drops can help relieve dry eyes. Try to get ones recommended by your doctor',
            'Make sure you screens are at least an arms length away from your eyes', 
            'Improve the air quality the air by getting a humidifier or adjusting the thermostat',
            'If you smoke, try to stop as it can lead to diseases related to vision loss',
            'Low levels of blue light (emitted froms screens and most lights) do not affect your eyes, but high levels can be hazardous to your eyes',
            'Blue light affects your biological clock (sleep cycle) so try to avoid screens and bright lights before or while you sleep',
            '20-20-20 Every 20 minutes focus at an object 20 feet far for at least 20 seconds', # done by timer
            '...'
        ]

        eye_tips_box = toga.Box(style=Pack(direction=COLUMN, padding_bottom=10, background_color='aqua')) 
        for tip in self.eye_tips:
            tip_box = MultilineLabel(tip, box_style=Pack(direction=COLUMN, padding_bottom=10, background_color='wheat'), 
                label_style=Pack(background_color='aqua', font_family='monospace', font_size=15), char_line=28)
            eye_tips_box.add(tip_box)

        eye_tips_scroll = toga.ScrollContainer(style=Pack(direction=COLUMN, padding=(5,5), background_color='red'))
        eye_tips_scroll.content = eye_tips_box

        # Calibrate box
        calibrate_box = toga.Box(style=Pack(direction=COLUMN, background_color='aqua'))
        calibrate_info = toga.Label('You will be given instructions',
            style=Pack(padding_left=10, padding_top=10, font_family='monospace', font_size=15))
        calibrate_button = toga.Button(
            'Calibrate',
            style=Pack(padding_left=50, padding_right=50, padding_top=20, padding_bottom=20,
                background_color='violet', font_family='monospace', font_size=20),
            on_press=self.start_calibrate
        )
        calibrate_when = MultilineLabel('Use this if you feel that blinks are not being counted correctly',
            box_style=Pack(direction=COLUMN, padding_bottom=10, background_color='aqua'),
            label_style=Pack(padding_left=10, font_family='monospace', font_size=15))

        calibrate_box.add(calibrate_when)
        calibrate_box.add(calibrate_button)
        calibrate_box.add(calibrate_info)

        # Config box
        config_box = toga.Box(style=Pack(direction=COLUMN, background_color='aqua'))
        self.video_switch = toga.Switch(
            'Show Video',
            style=Pack(padding_left=50, padding_right=50, padding_top=20, padding_bottom=20,
                font_family='monospace', font_size=20),
            is_on=self.tobool(self.read_config()[1])
        )

        save_button = toga.Button(
            'Save Configuration',
            style=Pack(padding_left=50, padding_right=50, padding_top=20, padding_bottom=20,
                background_color='violet', font_family='monospace', font_size=20),
            on_press=self.save_config
        )

        reset_button = toga.Button(
            'Reset Configuration',
            style=Pack(padding_left=50, padding_right=50, padding_top=20, padding_bottom=20,
                background_color='red', font_family='monospace', font_size=20),
            on_press=self.reset_config
        )

        config_box.add(self.video_switch)
        config_box.add(save_button)
        config_box.add(reset_button)
        
        # options - toolbar
        options = toga.OptionContainer(style=Pack(direction=ROW, background_color='snow', 
            font_family='monospace', font_size=15))
        options.add('Activity', activity_box)
        options.add('Eye tips', eye_tips_scroll)
        options.add('Calibrate', calibrate_box)
        options.add('Configure', config_box)

        main_box = toga.Box(style=Pack(padding=(10,10), direction=COLUMN, background_color='snow'))
        main_box.add(options)

        # Create and show main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(640,480), resizeable=False)
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
        fd.start_detection(BREAK_TIME=self.BREAK_TIME, DISPLAY_FRAME=self.video_switch.is_on, DISPLAY_TYPE='blink')

    # may replace with a python windows balloon tip notifier vvv
    # notifies the user with a dialog box
    def notify(self, widget):
        print('[App] Eye notification')
        text = 'It has been {:.1f} minutes, please take a {} second break\n'.format(self.CHECKUP_TIME/60.0, self.BREAK_TIME)
        text += 'You have blinked {} times\n'.format(fd.blink_count)
        text += 'Tip: ' + random.choice(self.eye_tips) + '\n'
        self.main_window.info_dialog('Eye Help', text)

    # save all config states to configuration file
    def save_config(self, widget):
        self.write_config(1, str(self.video_switch.is_on)) 

    # reset all config states in configuration file
    def reset_config(self, widget):
        config = open(self.CONFIG_FILE, 'w')
        config.write('0.25\n') # [0]: EAR_threshold for blink detection
        config.write('False\n') # [1]: Bool to turn on camera for general timer

    # writing to configuration file
    def write_config(self, idx, value):
        print('[App] Saving {} to config idx: {}'.format(value, idx))
        config_lines = self.read_config()
        config_lines[idx] = value + '\n'
        config = open(self.CONFIG_FILE, 'w')
        config.writelines(config_lines)
        config.close()

    # reading from configuration file
    def read_config(self):
        config = open(self.CONFIG_FILE, 'r')
        config_lines = config.readlines()
        config.close()
        return config_lines

    # helper function for converting string to bool
    def tobool(self, string): 
        return (string == 'True\n')

    # calibrate ear threshold
    def start_calibrate(self, widget):
        calibrate_thread = threading.Thread(target=calibrate.start_calibrate())

def main():
    return EyeHelp()
