import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response, request, flash, redirect, jsonify
from camera import VideoCamera
import time
import threading
import sqlite3
import os
import datetime, time
from threading import Thread
from django.shortcuts import render
from flask import Flask, redirect, url_for, render_template, request, session
# import cam 

email_update_interval = 50 
video_camera = VideoCamera()
camera_cv2 =  cv2.VideoCapture(0)
object_classifier = cv2.CascadeClassifier("models/upperbody_recognition_model.xml")


app = Flask(__name__)
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
global sessionx
def register_user_to_db(username, password):
    con = sqlite3.connect('db_web.db')
    cur = con.cursor()
    cur.execute('INSERT INTO users(username,password,email,name) values (?,?)', (username, password))
    con.commit()
    con.close()


def check_user(username, password):
    con = sqlite3.connect('db_web.db')
    cur = con.cursor()
    
    cur.execute('Select username,password, uid FROM users WHERE username=? and password=?', (username, password))

    result = cur.fetchone()
    
    if result:        
        return (True,result[2])
    else:
        return (False,0)


app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"


@app.route('/savedb',methods = ['POST', 'GET'])
def savedb():
    global conn
    if request.method == 'POST':
      try:
         name = request.form['name']
         email = request.form['email']        
         
         with sqlite3.connect("db_web.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE usercon SET name=?, email=? WHERE uid=1",(name,email))            
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         con.close()
         return render_template("result.html",msg = msg)         
 

         
def getTheEmail():
    con = sqlite3.connect('db_web.db')
    cursor = con.cursor()
    print("Opened database successfully")
    select_query = "SELECT * FROM usercon WHERE uid=1"
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
    global last_sent, sessionx
    while True:
        try:
            frame, found_obj = video_camera.get_object(object_classifier)
            if found_obj and (time.time() - last_sent) > email_update_interval:
                print("Sending...")
                last_sent = time.time()
                print(sessionx)
                # TO REMOVE
                # get the session userID
                # SESSION_ID = session['username']                 
                sendEmail(frame)
                print ("Email Sent...")
                
        except:
            # TO REMOVE
            
            print ("Error sending email: ", sys.exc_info()[0])
            print ("Error sending email: ", sys.exc_info())
            # pass    
# Deprecation For the meantime
# @app.route('/')
# def index():
#     email = getTheEmail()[2]
#     name = getTheEmail()[1]
#     return render_template('index.html', emailsend=email, name=name)

# initial page
@app.route("/")
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

# register page
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        register_user_to_db(username, password)
        return redirect(url_for('index'))
    elif 'username' in session:
        return redirect(url_for('home'))
    else:
        return render_template('register.html')
# login page
@app.route('/login', methods=["POST", "GET"])
def login():
    global sessionx
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(check_user(username, password))
        
        if check_user(username, password)[0]:
            # session the userID
            session['userid'] = check_user(username, password)[1]
            session['username'] = username
            sessionx = session['userid']
            # if username is admin add session admin
            if username == 'admin':
                session['admin'] = True
            return redirect(url_for('home'))
        return redirect(url_for('home'))
    # if user is already logged in
    elif 'username' in session:
        return redirect(url_for('home'))
    else:
        # check if username is null or password is null
        if(request.form['username'] == "" or request.form['password'] == ""):
            return render_template('login.html', msg="Please enter username and password")
        else:
            return render_template('login.html', msg="Not register in database")


@app.route('/home', methods=['POST', "GET"])
def home():
    if 'admin' in session:
       return render_template('index.html', admin=True)
    elif 'username' in session:
        return render_template('index.html', admin=False, username=session['username'], userid=session['userid'])
    else:
        return render_template('login.html', msg=True) 


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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


@app.route("/users")
def users():
    if 'admin' in session:
        con=sqlite3.connect("db_web.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from users")
        data=cur.fetchall()
        return render_template("users.html",datas=data)
    else:
        return redirect(url_for('index'))

@app.route("/add_user",methods=['POST','GET'])
def add_user():
    if 'admin' in session:
        if request.method=='POST':
            username=request.form['username']
            password=request.form['password']
            email=request.form['email']
            name=request.form['name']
            con=sqlite3.connect("db_web.db")
            cur=con.cursor()
            # if username is not in database, add it
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cur.fetchone() is None:
                cur.execute("insert into users (username,password,email,name) values(?,?,?,?)",(username,password,email,name))
                con.commit()
                con.commit()
                con.close()                
                flash('User Added','success')
                return redirect(url_for("users"))
                
            else:
                flash("Username already exist")
                return render_template("add_user.html")
            
        return render_template("add_user.html")
    else:
        return redirect(url_for('index'))

@app.route("/edit_user/<string:uid>",methods=['POST','GET'])
def edit_user(uid):
    if 'admin' in session:
        if request.method=='POST':
            username=request.form['username']
            password=request.form['password']
            email=request.form['email']
            name=request.form['name']
            con=sqlite3.connect("db_web.db")
            cur=con.cursor()
            # check if username is already in database
            cur.execute("select * from users where username=?",(username,))
            data=cur.fetchall()
            if not(len(data) > 0):
                flash('Username already in database','danger')
                return redirect(url_for("users"))
            else:
                cur.execute("update users set username=?,password=?,email=?,name=? where uid=?",(username,password,email,name,uid))
                con.commit()
                flash('User Updated','success')
                return redirect(url_for("users"))
            
        con=sqlite3.connect("db_web.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from users where UID=?",(uid,))
        data=cur.fetchone()
        return render_template("edit_user.html",datas=data)
    else:
        return redirect(url_for('index'))

    
@app.route("/delete_user/<string:uid>",methods=['GET'])
def delete_user(uid):
    if 'admin' in session:
        con=sqlite3.connect("db_web.db")
        cur=con.cursor()
        cur.execute("delete from users where UID=?",(uid,))
        con.commit()
        flash('User Deleted','warning')
        return redirect(url_for("users"))
    else:
        return redirect(url_for('index'))

@app.route("/edit_settings",methods=['POST','GET'])
def edit_settings():    
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        name=request.form['name']
        con=sqlite3.connect("db_web.db")
        cur=con.cursor()
        # get the userid from session
        
        # check if usrname is already in database
        cur.execute("select * from users where username=?",(username,))
        data=cur.fetchone()
        if data is None:            
            return redirect(url_for("edit_settings"))
        cur.execute("update users set username=?,password=?,email=?,name=? where uid=?",(username,password,email,name,session['userid']))

        con.commit()
        flash('User Updated','success')
        return redirect(url_for("edit_settings"))
    con=sqlite3.connect("db_web.db")
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("select * from users where UID=?",(session['userid'],))
    data=cur.fetchone()
    return render_template("edit_settings.html",datas=data)
########## CAMERAAAAA RECORDER ###################
'''
import threading

class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.cap = camera
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # print if the recording is started
        print("Recording started")
        print(f"TEST LINE 360: {fourcc}")
        self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                print("Writing frame")
                print(f"TEST LINE 368: {frame} {ret}")
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCameraX(object):
    def __init__(self):
        # Open a camera
        self.cap = camera_cv2
      
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
    
    def __del__(self):
        self.cap.release()
    
    def get_frame(self):
        ret, frame = self.cap.read()

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)

            # Record video
            # if self.is_record:
            #     if self.out == None:
            #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))
                
            #     ret, frame = self.cap.read()
            #     if ret:
            #         self.out.write(frame)
            # else:
            #     if self.out != None:
            #         self.out.release()
            #         self.out = None  

            return jpeg.tobytes()
      
        else:
            return None

    def start_record(self):
        self.is_record = True
        print("Recording started")
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap)
        print("Recording thread started")
        print(f"TEST LINE 420: {self.recordingThread}")
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False
        print("Recording stopped")
        if self.recordingThread != None:            
            self.recordingThread.stop()

            
    
############### VIDEO RECORDER ###################
video_camera_record = None
global_framex_c = None
@app.route('/recordx')
def indexcam():
    return render_template('recordx.html')

@app.route('/record_status', methods=['POST'])
def record_status():
    print("record_status")
    global video_camera_record 
    if video_camera_record == None:
        video_camera_record = VideoCameraX()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera_record.start_record()
        return jsonify(result="started")
    else:
        video_camera_record.stop_record()
        return jsonify(result="stopped")

def video_stream():
    global video_camera_record 
    global global_framex_c

    if video_camera_record == None:
        video_camera_record = VideoCameraX()
        
    while True:
        frame = video_camera_record.get_frame()
        print(f"TEST LINE 465: {frame}")
        if frame != None:
            global_framex_c = frame
            print(f"TEST LINE 460: {frame}")
            print("TEST LINE 461: ", global_framex_c)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            print("TEST LINE 473: ", global_framex_c)
            print("TEST LINE 474: ", frame)
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_framex_c + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
'''
############## MAIN #############################

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.secret_key='admin123'
    app.run(host='0.0.0.0', debug=False, threaded=True)
