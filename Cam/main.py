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
# register_user_to_db DEPRECATED
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
# def tasks() DEPRECATED to use and to be removed
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
            # Read the current frame from the video stream
            # and convert it to grayscale
            # (since our haar cascade classifier requires grayscale images)        
            frame, found_obj = video_camera.get_object(object_classifier)
            # Check if an object has been detected
            # if object has been detected, send an email
            # sessionx is the session id of the user
            if found_obj and (time.time() - last_sent) > email_update_interval:
                print("Sending...")
                last_sent = time.time()
                print(sessionx)                               
                sendEmail(frame, sessionx)
                print ("Email Sent...")
                
        except:           
            print ("Error sending email: ", sys.exc_info()[0])
            print ("Error sending email: ", sys.exc_info())
            # pass    


# initial page
@app.route("/")
def index():
    # if it is in session, redirect to home page
    # else redirect to login page    
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

# DEPRECATED
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
        # check if the user is in the database
        # the reason why it has [0] is because the check_user returns a tuple and the first element is the boolean
        # if the user is in the database, redirect to home page        
        if check_user(username, password)[0]:
            # session the userID
            # sessionx is the session id of the user
            # the reason why it has [1] is because the check_user returns a tuple and the second element is the userID
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
    global sessionx
    sessionx = session['userid']
    if 'admin' in session:
        # if admin is in session, redirect to admin page
       return render_template('index.html', admin=True)
    elif 'username' in session:
        # if the user is in the database, redirect to home page
        return render_template('index.html', admin=False, username=session['username'], userid=session['userid'])
    else:
        # if user is not logged in, redirect to login page
        return render_template('login.html', msg=True) 


@app.route('/logout')
def logout():
    # session.clear() is used to clear all the session
    session.clear()
    # after clearing the session, redirect to login page
    return redirect(url_for('index'))

# this is function to generate the video feed
def gen(camera, camv2s):
    global rec_frame
    while True:
        frame = camera.get_frame()
        frame_vid = camv2s.read()
        rec_frame = frame_vid
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# this is function view to display the video feed
@app.route('/video_feed')
def video_feed():
    global sessionx
    sessionx = session['userid']
    print("Starting")
    return Response(gen(video_camera, camera_cv2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# this route is to show all the users in the database
@app.route("/users")
def users():
    # it should be admin to access this page
    if 'admin' in session:
        # get all the users in the database
        con=sqlite3.connect("db_web.db")        
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from users")
        # after fetching using fetchall(), it will return a list of tuples
        data=cur.fetchall()
        # pass the list of tuples to the users.html
        return render_template("users.html",datas=data)
    else:
        return redirect(url_for('index'))
# this route is to add new user
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

# this route is to edit the user along with the user id
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

# this route is to delete the user along with the user id    
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

# this route can access by everyone
# this route is use to edit the profile or settings
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

############## MAIN #############################

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.secret_key='admin123'
    app.run(host='0.0.0.0', debug=False, threaded=True)
