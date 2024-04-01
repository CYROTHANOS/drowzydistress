from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
import dlib
from imutils import face_utils
import time
import pygame

app = Flask(__name__)
CORS(app)

pygame.mixer.init()

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

status = ""
start_time = time.time()
active_duration = 0.0
drowsy_duration = 0.0
sleeping_duration = 0.0
total_sleeping_duration = 0.0
sleep_threshold = 5
eye_aspect_ratio_threshold = 0.25

ALARM_SOUND_PATH = "alarm.wav"
alarm_on = False

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def process_frame(frame):
    global status, start_time, active_duration, drowsy_duration, sleeping_duration, total_sleeping_duration, alarm_on
    current_time = time.time()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    face_detected = len(faces) > 0
    if face_detected:
        for face in faces:
            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)
            left_eye = landmarks[36:42]
            right_eye = landmarks[42:48]
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            if ear < eye_aspect_ratio_threshold:
                sleeping_duration += current_time - start_time
                if sleeping_duration >= sleep_threshold:
                    status = "SLEEPING !!!"
                    if not alarm_on:
                        pygame.mixer.music.load(ALARM_SOUND_PATH)
                        pygame.mixer.music.play()
                        alarm_on = True
                else:
                    status = "Drowsy !"
            else:
                sleeping_duration = 0
                status = "Active"
        duration = current_time - start_time
        if status == "Active":
            active_duration += duration
        elif status == "Drowsy !":
            drowsy_duration += duration
        elif status == "SLEEPING !!!":
            total_sleeping_duration += duration
        start_time = current_time
    else:
        if status == "Active":
            active_duration += current_time - start_time
        elif status == "Drowsy !":
            drowsy_duration += current_time - start_time
        elif status == "SLEEPING !!!":
            total_sleeping_duration += current_time - start_time
        status = "No face detected"
    return status, active_duration, drowsy_duration, sleeping_duration, total_sleeping_duration, face_detected

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        status_text, _, _, _, _, face_detected = process_frame(frame)
        status_color = (0, 255, 0) if face_detected else (0, 0, 255)
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_alarm', methods=['POST'])
def stop_alarm():
    global alarm_on
    if alarm_on:
        pygame.mixer.music.stop()
        alarm_on = False
        return jsonify({"success": True, "message": "Alarm stopped successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Alarm is not currently playing"}), 400

@app.route('/timer')
def timer():
    total_duration = active_duration + drowsy_duration + total_sleeping_duration
    active_percentage = (active_duration / total_duration) * 100 if total_duration > 0 else 0
    drowsy_percentage = (drowsy_duration / total_duration) * 100 if total_duration > 0 else 0
    sleeping_percentage = (total_sleeping_duration / total_duration) * 100 if total_duration > 0 else 0
    return jsonify({
        "activeDuration": active_duration,
        "drowsyDuration": drowsy_duration,
        "sleepingDuration": total_sleeping_duration,
        "activePercentage": active_percentage,
        "drowsyPercentage": drowsy_percentage,
        "sleepingPercentage": sleeping_percentage
    })

if __name__ == "__main__":
    app.run(debug=True)
