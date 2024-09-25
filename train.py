import face_recognition
import numpy as np
import os
import pickle

def save_known_faces(known_face_encodings, known_face_names, filename):
    with open(filename, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)

def encode_images_from_folder(folder_path, encoding_file):
    known_face_encodings = []
    known_face_names = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_path = os.path.join(folder_path, file_name)
            image = face_recognition.load_image_file(image_path)
            
            face_encoding = face_recognition.face_encodings(image)
            
            if len(face_encoding) > 0:
                known_face_encodings.append(face_encoding[0])
                known_face_names.append(os.path.splitext(file_name)[0])
            else:
                print(f"No face found in {file_name}")

    save_known_faces(known_face_encodings, known_face_names, encoding_file)

folder_path = "static/uploads"
encoding_file = "files/face_model.pkl"

encode_images_from_folder(folder_path, encoding_file)
print("MODEL IS TRAINED")
