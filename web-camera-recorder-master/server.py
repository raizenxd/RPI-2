# use Flask to render a template, redirecting to another url, and creating a URL
from flask import Flask, render_template, Response, jsonify, request
# import the necessary packages
import camx as camx2

app = Flask(__name__)

video_camera_record = None
global_framex_c = None

# initialize this Flask app
@app.route('/')
def index():
    return render_template('recordx.html')

# this route is for recording video
@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera_record 
    # if the request method is POST (as by pressing record button), then read the record status
    # if there is no video camera, create one
    if video_camera_record == None:
        # this is the thread for recording video
        video_camera_record = camx2.VideoCamera()
    # this is use to read the record status
    json = request.get_json()
    status = json['status']
    # if the record status is true, then start recording
    if status == "true":
        video_camera_record.start_record()
        return jsonify(result="started")
    else:
        video_camera_record.stop_record()
        return jsonify(result="stopped")
# This function is generate the video frames for the video recording
def video_stream():    
    global video_camera_record 
    global global_framex_c
    if video_camera_record == None:
        video_camera_record = camx2.VideoCamera()
    # loop over frames from the output stream

    while True:
        # read the next frame from the stream and resize it
        frame = video_camera_record.get_frame()
        if frame != None:
            global_framex_c = frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_framex_c + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    # return the response generated along with the specific media
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)