import cv2
# from sys import platform
# from imutils.video.webcamvideostream import WebcamVideoStream
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

class VideoCamera(object):
    def __init__(self):
        # This code is for Windows users         
        # self.vs = WebcamVideoStream(src=0).start()  
        # This code is for Raspberry Pi users      
        self.vs = PiVideoStream().start()
        # This is time for camera to warm up        
        time.sleep(2.0)
    def __del__(self):
        # code for stopping camera
        self.vs.stop()

    def get_frame(self):
        # Capture frame-by-frame
        frame = self.vs.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        # Our operations on the frame come here It will return image in binary format
        return jpeg.tobytes()

    def get_object(self, classifier):
        # initialize the video stream and allow the cammera sensor to warmup        
        found_objects = False
        # loop over the frames from the video stream
        frame = self.vs.read().copy()
        # resize the frame, convert it to grayscale, and blur it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces in the grayscale frame
        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        # if objects are found,make found_objects True
        if len(objects) > 0:
            found_objects = True

        
        # OBJECT DETECTION RECTANGLE DRAWING
        # for (x, y, w, h) in objects:
        #    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


        # show the output frame
        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)




