import datetime
import cv2
import threading
# You can change the path to your own path
PATH = '/home/pi/Desktop/gdrive' 
class RecordingThread (threading.Thread):
    def __init__(self, name, camera):  
        # A thread is use for a separate flow of execution. This means thatyour program will have two things happening at onc
        threading.Thread.__init__(self)           
        self.name = name
        self.isRunning = True
        # Open a camera
        self.cap = camera
        # Initialize video recording environment
        # VideoWriter_fourcc(*'MJPG') is a four character code used to specify the video codec.
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # make file name with timestamp format like Nov-12-2018-11-12-00
        fileName = datetime.datetime.now().strftime("%b-%d-%Y-%H-%M-%S") + ".avi"
        # make full path with file name
        # self.out is for recorded video
        # VideoWriter is a class for writing video files or image sequences.
        # 640,480 is the size of the video
        # The First parameter is the name of the output file.
        # The second parameter is the fourcc code
        # The third parameter is the number of frames per second
        # The fourth parameter is the frame size
        self.out = cv2.VideoWriter(f'{PATH}/{fileName}',fourcc, 20.0, (640,480))

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self):
        # Open a camera
        # Open the first camera device
        self.cap = cv2.VideoCapture(0)
      
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
    
    def __del__(self):
        # Release camera
        # When everything done, release the capture
        self.cap.release()
    
    def get_frame(self):
        # Capture frame-by-frame
        ret, frame = self.cap.read()

        if ret:
            # Our operations on the frame come here
            # imendcode() returns a memory buffer encoded as a JPEG image            
            ret, jpeg = cv2.imencode('.jpg', frame)
            # Convert to bytes
            # the memory buffer is converted to a bytes object
            return jpeg.tobytes()
      
        else:
            return None

    def start_record(self):
        # Initialize video recording environment
        # make is_record True
        self.is_record = True
        # make recordingThread        
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap)
        # recordingThread start
        self.recordingThread.start()


    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()

            