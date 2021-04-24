'''
Use facial landmark detector to detect face and blinks
'''
# import packages
from scipy.spatial import distance
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import dlib
import cv2
import time
import os
import sys

# info needed in app.py
has_face = False
detect_exit = False
blink_count = 0 

# function for calculating eye aspect ratio based on given eye shape
# p0 = far left, p1 = up left, p2 = up right, p3 = far right, p4 = down right, p5 = down left
# EAR = ( |p1-p5| + |p2-p4| ) / ( 2 * |p0 - p3| )
def get_ear(eye):
    # distance between opposite landmarks
    vleft = distance.euclidean(eye[1], eye[5])
    vright = distance.euclidean(eye[2], eye[4])
    hcenter = distance.euclidean(eye[0], eye[3])

    return (vleft + vright) / (2.0 * hcenter)

def start_detection(BREAK_TIME=20, DISPLAY_FRAME=False, SAVE_EAR_DATA=False,
                    DISPLAY_TYPE='none', COUNTDOWN=10):
    print('[face_detect] Starting face detection') 
    global has_face
    global detect_exit 
    global blink_count
    
    # path for 68 facial landmarks predictor from http://dlib.net/
    ospath = os.path.dirname(sys.argv[0])
    SHAPE_PREDICTOR_FILE = ospath + '\\shape_predictor_68_face_landmarks.dat' 
    
    # constants
    EAR_MIN_FRAMES = 2 # minimum number of frames that must be closed to consider blink 
    MAX_FILE_SIZE = 1e4 # (around 10 kB) maximum data file size in bytes

    CONFIG_FILE = ospath + '\\config'
    config = open(CONFIG_FILE, 'r')
    config_lines = config.readlines() 
    EAR_THRESHOLD = float(config_lines[0].rstrip('\r\n')) # eye aspect ratio threshold, needs to be calibrated

    # counters
    blink_frame_count = 0 # number of frames eyes have been 'closed' for
    blink_count = 0 # number of blinks this session

    # manage loop
    has_face = False # true if no face for more than BREAK_TIME
    detect_exit = False

    # initialize left and right eye indexes of landmark detector
    LEFT_ID = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
    RIGHT_ID = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

    # initialize dlib face detector and facial landmark predictor
    face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_FILE) 

    # initialize data file to write to
    if SAVE_EAR_DATA:
        EAR_DATA_FILE = ospath + '\\EAR_data'
        ear_data = open(EAR_DATA_FILE, 'w')

    # start video stream
    video_stream = VideoStream(src=0).start()

    if DISPLAY_TYPE == 'calibrate':
        start_time = time.time()
        leftover_time = 5
        # instruct user
        while True:
            # resize video stream frame
            frame = video_stream.read()
            frame = imutils.resize(frame, width=400, height=400)
            cv2.rectangle(frame, (10,10), (390,390), (0,0,0), -1)
            
            # instructions                         
            cv2.putText(frame, 'Please keep your eyes open',
                        (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, 'during the callibration',
                        (15, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) 

            cv2.putText(frame, 'Press \'s\' to start'.format(leftover_time),
                        (15, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            cv2.imshow('Camera', frame)

            # exit using s key
            if (cv2.waitKey(1) & 0xFF) == ord('s') or detect_exit:
                break            

    # timers
    start_time = time.time()
    last_face = time.time()

    # main loop
    while True:
        # convert and resize current video stream frame
        frame = video_stream.read()
        frame = imutils.resize(frame, width=400, height=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # loop through faces on screen
        faces = face_detector(gray)
        
        # will count the total blinks of everybody if there are more than 1 user
        for face in faces:
            # predict facial landmarks and convert to numpy array
            shape = shape_predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            # get and calculate eye aspect ratios 
            left_eye = shape[LEFT_ID[0]:LEFT_ID[1]] 
            right_eye = shape[RIGHT_ID[0]:RIGHT_ID[1]] 
            left_EAR = get_ear(left_eye)
            right_EAR = get_ear(right_eye)
            avg_EAR = (left_EAR+right_EAR)/2.0
            
            # save eye aspect ratio on new line in text file
            if SAVE_EAR_DATA and ear_data.tell() < MAX_FILE_SIZE:
                ear_data.write(str(avg_EAR) + '\n')

            # when eye seems like a blink (both left and right EAR is below threshold)
            if avg_EAR <= EAR_THRESHOLD:
                # increase number of frames eye has been under EAR in succession
                blink_frame_count += 1
            else:
                # make sure eyes have been closed long enough to confirm it's a blink
                if blink_frame_count >= EAR_MIN_FRAMES:
                    # increase blink count
                    blink_count += 1
                    print('[face_detect] This is the {}th blink'.format(blink_count))
                # reset blink_frame_count because eyes are presumably open
                blink_frame_count = 0

            if DISPLAY_FRAME:
                # draw box around face with text
                cv2.rectangle(frame, (face.left(),face.top()+5), 
                    (face.right(),face.bottom()), (255,255,0), 1)

                left_hull = cv2.convexHull(left_eye)
                right_hull = cv2.convexHull(right_eye)
                cv2.drawContours(frame, [left_hull], -1, (0,255,0), 1)
                cv2.drawContours(frame, [right_hull], -1, (0,255,0), 1)

                cv2.putText(frame, 'EAR: {:.3f}'.format((left_EAR+right_EAR)/2.0), (face.left(), face.top()),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if DISPLAY_FRAME:
            # display leftover time
            if DISPLAY_TYPE == 'calibrate':
                leftover_time = COUNTDOWN - (time.time() - start_time)
                # since callibrating, exit window if no more time left
                if leftover_time <= 0:
                    detect_exit = True
                    break
                cv2.rectangle(frame, (0, 290), (400, 400), (0,0,0))
                cv2.putText(frame, 'Time left: {:.1f}'.format(leftover_time), (0, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
            # display time
            elif DISPLAY_TYPE == 'time':
                elapsed_time = time.time() - start_time
                cv2.rectangle(frame, (0, 290), (400, 400), (0,0,0))
                cv2.putText(frame, 'Time: {:.2f}'.format(elapsed_time), (0, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            # display blinks
            elif DISPLAY_TYPE == 'blink':
                cv2.rectangle(frame, (0, 290), (400, 400), (0,0,0))
                cv2.putText(frame, 'Blinks: {}'.format(blink_count), (0, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
            cv2.imshow('Camera', frame)

        # update has_face if no face seen for some time (BREAK_TIME)
        # print('[face_detect] faces {}'.format(len(faces)))
        if len(faces) > 0:
            last_face = time.time()
            has_face = True
        else:
            elapsed_time = time.time() - last_face
            if elapsed_time >= BREAK_TIME:
                has_face = False
                # break

        # force quit using q key
        if (cv2.waitKey(1) & 0xFF) == ord('q') or detect_exit:
            detect_exit = True
            break

    # cleanup
    cv2.destroyAllWindows() 
    if SAVE_EAR_DATA:
        ear_data.close()

    print('[face_detect] program terminated')

if __name__=='__main__':
    start_detection(BREAK_TIME=5, DISPLAY_FRAME=True, SAVE_EAR_DATA=True, 
        DISPLAY_TYPE='none')