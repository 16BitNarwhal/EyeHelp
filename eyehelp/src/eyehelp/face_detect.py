"""
Use facial landmark detector to detect if a face exists
"""
# import packages
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import dlib
import cv2
import time

# will be used to send info to app.py
can_see_face = False
def has_face():
    return can_see_face

def start_detection(CHECKUP_TIME=20*60, BREAK_TIME=20, DISPLAY_FRAME=False):
    
    # path for 68 facial landmarks predictor from http://dlib.net/
    SHAPE_PREDICTOR_FILE = 'eyehelp\src\eyehelp\shape_predictor_68_face_landmarks.dat'
    
    # initialize dlib face detector and facial landmark predictor
    face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_FILE)

    # start video stream
    video_stream = VideoStream(src=0).start()

    # timers
    start_time = time.time() 
    last_face = time.time()

    # main loop
    while True:
        # if CHECKUP_TIME is 0, don't use timer
        if CHECKUP_TIME > 0:
            # stop loop when program reaches elapsed_time 
            elapsed_time = time.time() - start_time
            if elapsed_time >= CHECKUP_TIME:
                break

        # convert and resize current video stream frame
        frame = video_stream.read()
        frame = imutils.resize(frame, width=400, height=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # loop through faces on screen
        faces = face_detector(gray)

        for face in faces:
            # predict facial landmarks and convert to numpy array
            shape = shape_predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            if DISPLAY_FRAME:
                # draw box around face with text
                cv2.rectangle(frame, (face.left(),face.top()+5), 
                    (face.right(),face.bottom()), (255,255,0), 1)
                cv2.putText(frame, "User", (face.left(), face.top()),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        if DISPLAY_FRAME:
            # display time
            elapsed_time = time.time() - start_time
            cv2.putText(frame, "Time: {:.2f}".format(elapsed_time), (0, 290),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Camera", frame)

        # update can_see_face if no face seen for some time (BREAK_TIME)
        if len(faces) > 0:
            last_face = time.time()
            can_see_face = True
        else:
            elapsed_time = time.time() - last_face
            if elapsed_time >= BREAK_TIME:
                can_see_face = False
                break

        # force quit using q key
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

if __name__=='__main__':
    start_detection(0, 5, True)