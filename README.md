# CivicReport Community Complaint Portal

A simple Flask + MySQL web app for registering users, submitting community complaints, and viewing complaint records.

## Features
- User registration and login
- Submit complaints with title, description, department, location, and optional photo URL
- View complaints for the logged-in user
- Store complaint data in MySQL

## Project Structure
- my_project.py - Flask backend API
- community_portal_full.html - Frontend complaint portal UI

## Requirements
Install the required Python packages:

```bash
pip install flask flask-cors mysql-connector-python
```

## Database Setup
1. Create a MySQL database named `Complaint_portal`.
2. Make sure your MySQL credentials match the values in `my_project.py`.
3. The app will create the required tables automatically when it starts.

## Run the Application
From the project folder, run:

```bash
python my_project.py
```

Then open the frontend page in your browser.

## Notes
- The app uses MySQL for persistent complaint storage.
- The backend runs on http://127.0.0.1:5000

## GitHub Upload
1. Initialize git if needed:
   ```bash
   git init
   ```
2. Add files:
   ```bash
   git add .
   ```
3. Commit:
   ```bash
   git commit -m "Initial commit"
   ```
4. Push to your GitHub repository.
