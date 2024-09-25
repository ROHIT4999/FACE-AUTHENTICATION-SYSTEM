import os
import subprocess
from flask import Flask, jsonify, request, render_template, redirect, url_for, Response, session
import face_recognition
import MySQLdb
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import pickle
import mysql.connector
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="faceauth"
)
cursor = db.cursor()

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        photo = request.files['photo']
        uploads_folder = os.path.join(app.static_folder, "uploads")

        if not os.path.exists(uploads_folder):
            os.makedirs(uploads_folder)

        photo_filename = f'{name}.jpg'
        photo_path = os.path.join(uploads_folder, photo_filename)
        photo.save(photo_path)

        try:
            cursor.execute("INSERT INTO users (name, photo_filename) VALUES (%s, %s)", (name, photo_filename))
            db.commit()

            # Run the training script
            subprocess.run(['python', 'train.py'], check=True)
            
            return jsonify({"success": True, "redirect": url_for('login')})
        except MySQLdb.IntegrityError:
            return jsonify({"success": False, "message": "User already exists"})

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        photo = request.files['photo']
        login_folder = os.path.join(app.static_folder, "login")

        if not os.path.exists(login_folder):
            os.makedirs(login_folder)

        login_filename = os.path.join(login_folder, "login_face.jpg")
        photo.save(login_filename)

        login_image = face_recognition.load_image_file(login_filename)
        login_face_encodings = face_recognition.face_encodings(login_image)

        cursor.execute("SELECT name, photo_filename FROM users")
        users = cursor.fetchall()

        for name, filename in users:
            registered_photo = os.path.join(app.static_folder, "uploads", filename)
            registered_image = face_recognition.load_image_file(registered_photo)
            registered_face_encodings = face_recognition.face_encodings(registered_image)

            if len(registered_face_encodings) > 0 and len(login_face_encodings) > 0:
                matches = face_recognition.compare_faces(registered_face_encodings, login_face_encodings[0])

                if any(matches):
                    session['user_name'] = name  # Store username in session
                    return jsonify({"success": True, "name": name, "image_path": filename})

        return jsonify({"success": False, "message": "No matching face found"})

    return render_template("login.html")

@app.route("/success")
def success():
    name = request.args.get('name')
    image_path = request.args.get('image_path')
    return render_template("success.html", name=name, image_path=image_path)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/diagnose")
def diagnose():
    return render_template("diagnose.html")

@app.route("/start_diagnose", methods=["POST"])
def start_diagnose():
    # Trigger the diagnosis process
    return jsonify({"success": True})

@app.route("/finish_diagnose", methods=["POST"])
def finish_diagnose():
    # Indicate that the diagnosis process is completed and show the chatbot button
    return jsonify({"success": True})

@app.route("/chatbot", methods=["GET"])
def chatbot():
    user_name = session.get('user_name')  # Get the stored user name from the session
    if user_name:
        emotion = get_common_emotion(user_name)
        return render_template('chatbot.html', question=f"You seem to be {emotion}.. right!!! ")
    return jsonify({"error": "User not recognized"})

@app.route('/chatbot_response', methods=['POST'])
def chatbot_response():
    data = request.get_json()
    user_response = data.get('response')
    
    # Simulate processing the response
    if user_response:
        if user_response.lower() == 'yes':
            return jsonify({"redirect": "/other_page"})
        elif user_response.lower() == 'no':
            return jsonify({"redirect": "/another_page"})
        else:
            return jsonify({"error": "Unexpected response"}), 400
    else:
        return jsonify({"error": "No response provided"}), 400


def load_known_faces(filename):
    with open(filename, 'rb') as f:
        known_face_encodings, known_face_names = pickle.load(f)
    return known_face_encodings, known_face_names

def load_emotion_model(model_path):
    return load_model(model_path)

# Load the known face encodings and names
encodeListKnown, classNames = load_known_faces('files/face_model.pkl')
print(len(encodeListKnown))
print('Encoding Complete')

# Load the classifiers and emotion model
face_classifier = cv2.CascadeClassifier('files/haarcascade_frontalface_default.xml')
eye_classifier = cv2.CascadeClassifier('files/haarcascade_eye.xml')
smile_classifier = cv2.CascadeClassifier('files/haarcascade_smile.xml')
emotion_model = load_emotion_model('files/EMOTION_MODEL.h5')
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

def generate_frames():
    cap = cv2.VideoCapture(0)
    start_time = datetime.datetime.now()

    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            username_stored = False

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = f"{classNames[matchIndex].upper()}"
                else:
                    name = "UNKNOWN"

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (36, 255, 12), 2)
                cv2.putText(img, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                if name != "UNKNOWN" and not username_stored:
                    elapsed_time = datetime.datetime.now() - start_time

                    if elapsed_time.total_seconds() >= 10:
                        print("10 seconds elapsed. Stopping recognition.")
                        username_stored = True
                        break

                    roi_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    roi_gray = roi_gray[y1:y2, x1:x2]
                    roi_gray = cv2.resize(roi_gray, (48, 48))
                    roi_gray = roi_gray / 255.0
                    roi_gray = np.reshape(roi_gray, (1, 48, 48, 1))

                    prediction = emotion_model.predict(roi_gray)
                    label = emotion_labels[np.argmax(prediction)]
                    cv2.putText(img, label, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 95, 255), 2)
                    
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        connection = mysql.connector.connect(
                            host='localhost',
                            database='faceauth',
                            user='root',
                            password=''
                        )
                        mySql_insert_query = ("""INSERT INTO recognized_faces(username, emotion, time) 
                                                VALUES(%s, %s, %s)""", 
                                              (name, label, current_time,))

                        cursor = connection.cursor()
                        cursor.execute(*mySql_insert_query)
                        connection.commit()
                        cursor.close()
                        username_stored = True

                    except mysql.connector.Error as error:
                        print("Failed to insert record into user table {}".format(error))

                    finally:
                        if connection.is_connected():
                            connection.close()
                            break

                roi_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                roi_gray = roi_gray[y1:y2, x1:x2]
                roi_gray = cv2.resize(roi_gray, (48, 48))
                roi_gray = roi_gray / 255.0
                roi_gray = np.reshape(roi_gray, (1, 48, 48, 1))

                prediction = emotion_model.predict(roi_gray)
                label = emotion_labels[np.argmax(prediction)]
                cv2.putText(img, label, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 95, 255), 2)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def get_common_emotion(username):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='faceauth',
            user='root',
            password=''
        )

        sql_query = "SELECT emotion, COUNT(emotion) AS count FROM recognized_faces WHERE username = %s GROUP BY emotion ORDER BY count DESC LIMIT 1"
        cursor = connection.cursor()
        cursor.execute(sql_query, (username,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return "Neutral"

    except mysql.connector.Error as error:
        print("Failed to retrieve common emotion: {}".format(error))
        return "Neutral"

    finally:
        if connection.is_connected():
            connection.close()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/other_page")
def other_page():
    return render_template("other_page.html")
@app.route("/another_page")
def another_page():
    return render_template("another_page.html")
if __name__ == "__main__":
    app.run(debug=True)
