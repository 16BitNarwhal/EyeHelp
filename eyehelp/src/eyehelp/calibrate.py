'''
Determine recommended EAR for detect blinks
'''
# import packages
import os
import sys
import eyehelp.face_detect as fd

def start_calibrate():
    # initiate files
    ospath = os.path.dirname(sys.argv[0])
    EAR_DATA_FILE = ospath + '\\EAR_data'
    CONFIG_FILE = ospath + '\\config'

    # call face_detect
    print('[calibrate] Start calibrating')
    fd.start_detection(DISPLAY_FRAME=True, SAVE_EAR_DATA=True,
        DISPLAY_TYPE='calibrate', COUNTDOWN=2)
    
    # read EAR data
    ear_data = open(EAR_DATA_FILE, 'r') 
    blink_ear_data = [float(i) for i in ear_data.readlines()]
    blink_ear = min(blink_ear_data) + 0.02 # some offset
    ear_data.close()

    print('[calibrate] New blink threshold: {}'.format(blink_ear))

    # save new ata
    config = open(CONFIG_FILE, 'r')
    config_lines = config.readlines()
    config_lines[0] = str(blink_ear) + '\n'

    config = open(CONFIG_FILE, 'w')
    config.writelines(config_lines)
    config.close()

if __name__=='__main__':
    start_calibrate()
 