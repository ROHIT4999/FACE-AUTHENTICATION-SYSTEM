-- Create the database
CREATE DATABASE IF NOT EXISTS faceauth;

-- Use the database
USE faceauth;

-- Create the users table to store registered users' information
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    photo_filename VARCHAR(255) NOT NULL
);

-- Create the recognized_faces table to store recognized faces and their emotions
CREATE TABLE IF NOT EXISTS recognized_faces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    emotion VARCHAR(255) NOT NULL,
    time DATETIME NOT NULL,
    FOREIGN KEY (username) REFERENCES users(name)
);

