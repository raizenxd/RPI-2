import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response, request
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading
import sqlite3
import os
import datetime, time
from threading import Thread

email_update_interval = 50 
video_camera = VideoCamera()
camera_cv2 =  cv2.VideoCapture(0)
object_classifier = cv2.CascadeClassifier("models/upperbody_recognition_model.xml")


app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'user'
app.config['BASIC_AUTH_PASSWORD'] = 'pass'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
last_sent = 0

try:
    os.mkdir('./shots')
except OSError as error:
    pass
global capture,rec_frame, grey, switch, neg, face, out
global rec
capture=0
grey=0
neg=0
face=0
switch=1
rec=0


conn = sqlite3.connect('database.db')
print("Opened database successfully");

conn.execute("CREATE TABLE IF NOT EXISTS usercon (id INT, name TEXT, email TEXT);")
print("Table created successfully")
conn.close()

@app.route('/savedb',methods = ['POST', 'GET'])
def savedb():
    global conn
    if request.method == 'POST':
      try:
         name = request.form['name']
         email = request.form['email']        
         
         with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE usercon SET name=?, email=? WHERE id=1",(name,email))            
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         con.close()
         return render_template("result.html",msg = msg)         
         
def getTheEmail():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    print("Opened database successfully")
    select_query = "SELECT * FROM usercon WHERE id=1"
    cursor.execute(select_query)
    records = cursor.fetchone()
    print(records)
    return (records)
    cursor.close()
    
def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)
@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':   
        if  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                          
                 
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')
def check_for_objects():
    global last_sent
    while True:
        try:
            frame, found_obj = video_camera.get_object(object_classifier)
            if found_obj and (time.time() - last_sent) > email_update_interval:
                print("Sending...")
                last_sent = time.time()
                sendEmail(frame)
                print ("Email Sent...")
                
        except:
            print ("Error sending email: ", sys.exc_info()[0])

@app.route('/')
@basic_auth.required
def index():
    email = getTheEmail()[2]
    name = getTheEmail()[1]
    return render_template('index.html', emailsend=email, name=name)

def gen(camera, camv2s):
    global rec_frame
    while True:
        frame = camera.get_frame()
        frame_vid = camv2s.read()
        rec_frame = frame_vid
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    print("Starting")
    return Response(gen(video_camera, camera_cv2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False)
