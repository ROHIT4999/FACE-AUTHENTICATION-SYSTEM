# facial-authentication

Facial Login System

The Facial Login System is a secure and user-friendly application that allows users to log into a system using facial recognition. Instead of relying on traditional login methods like passwords or PINs, the system identifies users based on their facial features using real-time face recognition. This technology is becoming popular in personal devices, workplaces, and high-security environments due to its ease of use and the increased security it provides over password-based systems.

Features of the Facial Login System:

Face Registration: Users can register their face with the system. During registration, the system captures the user's face, processes it, and stores the unique face encodings in a database for future recognition.

Face Authentication: When a user attempts to log in, the system compares their face with the stored face encodings to verify their identity. If the face is recognized, the user is granted access.

Database Integration: The system integrates with a MySQL database to store user information and facial encoding data securely.

Real-Time Face Detection: Utilizes OpenCV for real-time face detection and recognition, allowing the system to identify users quickly and accurately.

Security: Facial recognition provides an additional layer of security as it is harder to duplicate or steal compared to traditional credentials like passwords.

Web-Based Interface: The system can be accessed through a web browser, allowing users to log in from various devices connected to the network.

Cross-Platform: Can be deployed on different platforms (Windows, Linux, etc.) with a webcam or camera-enabled device.

Technologies Used:

Python: The core programming language for implementing the facial recognition logic.

OpenCV: Used for capturing video streams, detecting faces, and processing images.

Face Recognition Library: A Python library built on deep learning techniques to encode and match faces.

Flask: A lightweight web framework to create the login interface and serve the facial recognition functionality over a network.

MySQL: A relational database used to store user details and facial encodings securely.

NumPy: For array operations related to image and face processing.

Pillow (PIL): For handling image conversion in Python.

System Workflow:

1. Face Registration:

Face Capture: A user sits in front of a camera, and their face is captured using the webcam.

Face Encoding: The system converts the facial features into a numerical encoding using a deep learning-based face recognition algorithm.

Database Storage: The encoding, along with the user's login information (e.g., username or ID), is stored in a MySQL database for future authentication.

2. Face Authentication (Login):

Live Face Capture: The system captures the user's face in real-time when they try to log in.

Face Comparison: The system compares the captured face's encoding with the stored encodings in the database.

Authentication Result: If a match is found, the user is authenticated and granted access to the system. If no match is found, access is denied.

3. Access Granted/Denied:

If the system recognizes the user, it logs them in and allows access to the system (e.g., a protected dashboard or application).
If the system does not recognize the face, it displays an error message and denies access.

Setup Procedure:

1.Download the zip file and extract it in desired location.
2.Install the required packages using pip install -r requirements.txt.
3.Setup up the database by importing the sql file in the MySQL(phpMyAdmin) through Xampp Control Panel.
4.Run the application using "python app.py" in the command line.

