from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Allow frontend HTML to call the API

# ─── MySQL Configuration ──────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",         # Change to your MySQL username
    "password": "Gubendhir@n10",  # Change to your MySQL password
    "database": "Complaint_portal"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ─── Create Database & Tables ─────────────────────────────────────────────────
def init_db():
    # First connect without database to create it
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS Complaint_portal")
    cur.execute("USE Complaint_portal")

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            location VARCHAR(200),
            photo VARCHAR(500),
            department VARCHAR(100),
            status VARCHAR(50) DEFAULT 'Pending',
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database and tables ready.")

init_db()


# ─── User Registration ────────────────────────────────────────────────────────
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    hashed = generate_password_hash(data['password'])

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (data['username'], hashed)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User Registered Successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409


# ─── User Login ───────────────────────────────────────────────────────────────
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user['password'], data['password']):
        return jsonify({"message": "Login Successful", "user_id": user['id'], "username": user['username']}), 200
    return jsonify({"error": "Invalid Credentials"}), 401


# ─── Submit Complaint ─────────────────────────────────────────────────────────
@app.route('/report', methods=['POST'])
def report():
    data = request.json
    required = ['title', 'description', 'location', 'department']
    for field in required:
        if not data or not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO complaints (user_id, title, description, location, photo, department)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        data.get('user_id'),
        data['title'],
        data['description'],
        data['location'],
        data.get('photo', ''),
        data['department']
    ))
    conn.commit()
    complaint_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"message": "Complaint Submitted", "id": complaint_id}), 201


# ─── View All Complaints (Admin) ──────────────────────────────────────────────
@app.route('/complaints', methods=['GET'])
def complaints():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute('''
        SELECT c.*, u.username FROM complaints c
        LEFT JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    ''')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Convert datetime to string for JSON
    for row in rows:
        if row.get('created_at'):
            row['created_at'] = str(row['created_at'])
    return jsonify(rows), 200


# ─── View My Complaints ───────────────────────────────────────────────────────
@app.route('/my_complaints/<int:user_id>', methods=['GET'])
def my_complaints(user_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        if row.get('created_at'):
            row['created_at'] = str(row['created_at'])
    return jsonify(rows), 200


# ─── Update Status (Admin) ────────────────────────────────────────────────────
@app.route('/update_status/<int:id>', methods=['PUT'])
def update_status(id):
    data = request.json
    if not data or not data.get('status'):
        return jsonify({"error": "Status is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE complaints SET status = %s WHERE id = %s", (data['status'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Status Updated"}), 200


# ─── Add Feedback ─────────────────────────────────────────────────────────────
@app.route('/feedback/<int:id>', methods=['PUT'])
def feedback(id):
    data = request.json
    if not data or not data.get('feedback'):
        return jsonify({"error": "Feedback is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE complaints SET feedback = %s WHERE id = %s", (data['feedback'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Feedback Saved"}), 200


if __name__ == "__main__":
    app.run(debug=False, port=5000)
