from flask import Flask, render_template, Response, jsonify, request
import camx as camx2

app = Flask(__name__)

video_camera_record = None
global_framex_c = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera_record 
    if video_camera_record == None:
        video_camera_record = camx2.VideoCamera()

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
        video_camera_record = camx2.VideoCamera()
        
    while True:
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
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)