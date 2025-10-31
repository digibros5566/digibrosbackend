# from flask import Flask, request, jsonify
# from flask_cors import CORS  # ✅ Import CORS
# import sqlite3

# app = Flask(__name__)  # ✅ Create the app first
# CORS(app, origins=["http://localhost:3000"])  # ✅ Then enable CORS
# CORS(app, origins=["http://localhost:3001"])  # ✅ Then enable CORS

# DATABASE = 'contacts.db'

# # Initialize DB
# def init_db():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS contacts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL,
#                 email TEXT NOT NULL,
#                 interest TEXT,
#                 message TEXT
#             )
#         ''')
#         conn.commit()

# # Insert new contact
# def insert_contact(name, email, interest, message):
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO contacts (name, email, interest, message) VALUES (?, ?, ?, ?)',
#                        (name, email, interest, message))
#         conn.commit()
#         return cursor.lastrowid

# # Get all contacts
# def get_all_contacts():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT id, name, email, interest, message FROM contacts')
#         rows = cursor.fetchall()
#         return [
#             {'id': row[0], 'name': row[1], 'email': row[2], 'interest': row[3], 'message': row[4]}
#             for row in rows
#         ]

# # Create new contact (from form)
# # @app.route('/api/contacts', methods=['POST'])
# # def create_contact():
# #     try:
# #         data = request.get_json()
# #         name = data.get('name')
# #         email = data.get('email')
# #         interest = data.get('service') or data.get('interest')
# #         message = data.get('message')

# #         if not name or not email:
# #             return jsonify({'error': 'Name and Email are required'}), 400

# #         contact_id = insert_contact(name, email, interest, message)
# #         return jsonify({'name': row[4], 'contact_id': contact_id,'email': row[0]}), 201

# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500


# @app.route('/api/contacts', methods=['POST'])
# def create_contact():
#     """Insert a new contact into the database"""
#     try:
#         data = request.get_json()
#         name = data.get('name')
#         email = data.get('email')
#         service = data.get('service') or data.get('interest')
#         message = data.get('message')

#         # Basic validation
#         if not name or not email:
#             return jsonify({'error': 'Name and Email are required'}), 400

#         with sqlite3.connect(DATABASE) as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 INSERT INTO contacts (name, email, interest, message)
#                 VALUES (?, ?, ?, ?)
#             ''', (name, email, service, message))
#             conn.commit()

#             contact_id = cursor.lastrowid

#             return jsonify({
#                 'contact_id': contact_id,
#                 'name': name,
#                 'email': email,
#                 'service': service,
#                 'message': message
#             }), 201

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # Get all contacts
# @app.route('/contacts', methods=['GET'])
# def list_contacts():
#     contacts = get_all_contacts()
#     return jsonify(contacts)

# # Run the app
# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import sqlite3
# from transformers import pipeline
# import hashlib

# # ------------------- APP SETUP -------------------
# app = Flask(__name__)
# CORS(app)
# DATABASE = 'contacts.db'

# # Load Emotion Model
# emotion_classifier = pipeline(
#     "text-classification",
#     model="j-hartmann/emotion-english-distilroberta-base",
#     return_all_scores=True
# )

# # ------------------- DATABASE INIT -------------------
# def init_db():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         # Contacts table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS contacts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL,
#                 email TEXT NOT NULL,
#                 interest TEXT,
#                 message TEXT
#             )
#         ''')
#         # Registration table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS register (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT,
#                 phone TEXT,
#                 email TEXT UNIQUE,
#                 password TEXT
#             )
#         ''')
#         # Feedback table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS feedback (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT,
#                 email TEXT,
#                 rating INTEGER,
#                 comment TEXT,
#                 emotion TEXT,
#                 submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')
#         # Emotions table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS emotions (
#                 email TEXT,
#                 text TEXT,
#                 emotion TEXT
#             )
#         ''')
#         conn.commit()

# # ------------------- UTILITIES -------------------
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def predict_emotion(text):
#     if not text or not text.strip():
#         return "neutral"
#     scores = emotion_classifier(text)[0]
#     top_emotion = max(scores, key=lambda x: x['score'])['label'].lower()
#     emotion_map = {
#         "joy": "happiness", "love": "love", "anger": "anger", "fear": "worry",
#         "surprise": "surprise", "sadness": "sadness", "disgust": "hate",
#         "neutral": "neutral", "enthusiasm": "enthusiasm", "boredom": "boredom",
#         "relief": "relief", "empty": "empty", "fun": "fun", "hate": "hate"
#     }
#     return emotion_map.get(top_emotion, "neutral")

# # ------------------- AUTH ROUTES -------------------
# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     name = data.get('name')
#     phone = data.get('phone')
#     email = data.get('email')
#     password = data.get('password')
#     re_password = data.get('re_password')

#     if not all([name, phone, email, password, re_password]):
#         return jsonify({'error': 'All fields are required'}), 400
#     if password != re_password:
#         return jsonify({'error': 'Passwords do not match'}), 400

#     hashed_pw = hash_password(password)
#     try:
#         with sqlite3.connect(DATABASE) as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 INSERT INTO register (name, phone, email, password)
#                 VALUES (?, ?, ?, ?)
#             ''', (name, phone, email, hashed_pw))
#             conn.commit()
#         return jsonify({'message': 'User registered successfully'}), 201
#     except sqlite3.IntegrityError:
#         return jsonify({'error': 'Email already exists'}), 409

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     if not email or not password:
#         return jsonify({'error': 'Email and password are required'}), 400

#     hashed_pw = hash_password(password)
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT name, email, password FROM register WHERE email = ?', (email,))
#         row = cursor.fetchone()
#         if row and row[2] == hashed_pw:
#             return jsonify({'message': 'Login successful', 'name': row[0], 'email': row[1]}), 200
#         else:
#             return jsonify({'error': 'Invalid email or password'}), 401

# @app.route('/users', methods=['GET'])
# def list_users():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT id, name, phone, email FROM register')
#         users = [{'id': r[0], 'name': r[1], 'phone': r[2], 'email': r[3]} for r in cursor.fetchall()]
#     return jsonify(users)

# # ------------------- CONTACT ROUTES -------------------
# @app.route('/api/contacts', methods=['POST'])
# def create_contact():
#     data = request.get_json()
#     name, email = data.get('name'), data.get('email')
#     interest = data.get('service') or data.get('interest')
#     message = data.get('message')
#     if not name or not email:
#         return jsonify({'error': 'Name and Email are required'}), 400
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO contacts (name, email, interest, message) VALUES (?, ?, ?, ?)',
#                        (name, email, interest, message))
#         conn.commit()
#     return jsonify({'message': 'Contact saved successfully'}), 201

# @app.route('/contacts', methods=['GET'])
# def list_contacts():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT id, name, email, interest, message FROM contacts')
#         rows = cursor.fetchall()
#     return jsonify([{'id': r[0], 'name': r[1], 'email': r[2], 'interest': r[3], 'message': r[4]} for r in rows])

# # ------------------- FEEDBACK ROUTES -------------------
# @app.route('/feedback', methods=['POST'])
# def submit_feedback():
#     data = request.get_json()
#     name = data.get('name')
#     email = data.get('email')
#     rating = data.get('rating')
#     comment = data.get('comment', '')
#     if not all([name, email, rating]):
#         return jsonify({'error': 'Name, email, and rating are required'}), 400
#     emotion = predict_emotion(comment)
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO feedback (name, email, rating, comment, emotion) VALUES (?, ?, ?, ?, ?)',
#                        (name, email, rating, comment, emotion))
#         cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
#                        (email, comment, emotion))
#         conn.commit()
#     return jsonify({'message': 'Feedback submitted', 'emotion': emotion}), 201

# @app.route('/feedback', methods=['GET'])
# def get_feedback():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             SELECT f.id, f.name, f.email, f.rating, f.comment, f.submitted_at, e.emotion
#             FROM feedback f
#             LEFT JOIN emotions e ON f.email = e.email
#             ORDER BY f.submitted_at DESC
#         ''')
#         rows = cursor.fetchall()
#     return jsonify([{'id': r[0], 'name': r[1], 'email': r[2], 'rating': r[3], 'comment': r[4],
#                      'submitted_at': r[5], 'emotion': r[6]} for r in rows])

# # ------------------- EMOTION STATS -------------------
# @app.route('/records', methods=['GET'])
# def get_emotion_stats():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT emotion, COUNT(*) FROM emotions GROUP BY emotion')
#         rows = cursor.fetchall()
#     all_emotions = ["boredom","anger","empty","enthusiasm","fun","happiness",
#                     "hate","love","neutral","relief","sadness","surprise","worry"]
#     result = {e:0 for e in all_emotions}
#     for emotion, count in rows:
#         if emotion in result:
#             result[emotion] += count
#     return jsonify([{"emotion":"All Emotions", **result}])

# @app.route('/combined-emotion-count', methods=['GET'])
# def combined_emotion_count():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             SELECT emotion, COUNT(*) AS count
#             FROM (
#                 SELECT emotion FROM emotions
#                 UNION ALL
#                 SELECT emotion FROM feedback
#             ) AS combined
#             GROUP BY emotion
#             ORDER BY count DESC
#         ''')
#         rows = cursor.fetchall()
#     return jsonify([{'emotion': r[0], 'count': r[1]} for r in rows])

# # ------------------- RUN APP -------------------
# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import sqlite3
# from transformers import pipeline
# import hashlib

# # ------------------- APP SETUP -------------------
# app = Flask(__name__)
# CORS(app)
# DATABASE = 'contacts.db'

# # Load Emotion Model
# emotion_classifier = pipeline(
#     "text-classification",
#     model="j-hartmann/emotion-english-distilroberta-base",
#     return_all_scores=True
# )

# # ------------------- DATABASE INIT -------------------
# def init_db():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         # Contacts table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS contacts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL,
#                 email TEXT NOT NULL,
#                 interest TEXT,
#                 message TEXT
#             )
#         ''')
#         # Registration table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS register (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT,
#                 phone TEXT,
#                 email TEXT UNIQUE,
#                 password TEXT
#             )
#         ''')
#         # Feedback table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS feedback (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT,
#                 email TEXT,
#                 rating INTEGER,
#                 comment TEXT,
#                 emotion TEXT,
#                 submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
#             )
#         ''')
#         # Emotions table
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS emotions (
#                 email TEXT,
#                 text TEXT,
#                 emotion TEXT
#             )
#         ''')
#         conn.commit()

# # ------------------- UTILITIES -------------------
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def predict_emotion(text):
#     if not text or not text.strip():
#         return "neutral"
#     scores = emotion_classifier(text)[0]
#     top_emotion = max(scores, key=lambda x: x['score'])['label'].lower()
#     emotion_map = {
#         "joy": "happiness", "love": "love", "anger": "anger", "fear": "worry",
#         "surprise": "surprise", "sadness": "sadness", "disgust": "hate",
#         "neutral": "neutral", "enthusiasm": "enthusiasm", "boredom": "boredom",
#         "relief": "relief", "empty": "empty", "fun": "fun", "hate": "hate"
#     }
#     return emotion_map.get(top_emotion, "neutral")

# # ------------------- CONTACT ROUTES -------------------
# @app.route('/api/contacts', methods=['POST'])
# def create_contact():
#     data = request.get_json()
#     name, email = data.get('name'), data.get('email')
#     interest = data.get('service') or data.get('interest')
#     message = data.get('message')

#     if not name or not email:
#         return jsonify({'error': 'Name and Email are required'}), 400

#     emotion = predict_emotion(message)

#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO contacts (name, email, interest, message) VALUES (?, ?, ?, ?)',
#                        (name, email, interest, message))
#         cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
#                        (email, message, emotion))
#         conn.commit()

#     return jsonify({'message': 'Contact saved successfully', 'emotion': emotion}), 201

# @app.route('/contacts', methods=['GET'])
# def list_contacts():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('SELECT id, name, email, interest, message FROM contacts')
#         rows = cursor.fetchall()
#     return jsonify([{'id': r[0], 'name': r[1], 'email': r[2], 'interest': r[3], 'message': r[4]} for r in rows])

# # ------------------- FEEDBACK ROUTES -------------------
# @app.route('/feedback', methods=['POST'])
# def submit_feedback():
#     data = request.get_json()
#     name = data.get('name')
#     email = data.get('email')
#     rating = data.get('rating')
#     comment = data.get('comment', '')

#     if not all([name, email, rating]):
#         return jsonify({'error': 'Name, email, and rating are required'}), 400

#     emotion = predict_emotion(comment)

#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO feedback (name, email, rating, comment, emotion) VALUES (?, ?, ?, ?, ?)',
#                        (name, email, rating, comment, emotion))
#         cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
#                        (email, comment, emotion))
#         conn.commit()

#     return jsonify({'message': 'Feedback submitted', 'emotion': emotion}), 201

# @app.route('/feedback', methods=['GET'])
# def get_feedback():
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#             SELECT f.id, f.name, f.email, f.rating, f.comment, f.submitted_at, e.emotion
#             FROM feedback f
#             LEFT JOIN emotions e ON f.email = e.email
#             ORDER BY f.submitted_at DESC
#         ''')
#         rows = cursor.fetchall()
#     return jsonify([{'id': r[0], 'name': r[1], 'email': r[2], 'rating': r[3], 'comment': r[4],
#                      'submitted_at': r[5], 'emotion': r[6]} for r in rows])

# # ------------------- COMBINED RECORDS API -------------------
# @app.route('/records', methods=['GET'])
# def get_combined_records():
#     """Combine contact messages and feedback comments into one emotion count"""
#     with sqlite3.connect(DATABASE) as conn:
#         cursor = conn.cursor()
#         # Fetch contact messages
#         cursor.execute('SELECT email, message FROM contacts')
#         contacts = cursor.fetchall()
#         # Fetch feedback comments
#         cursor.execute('SELECT email, comment FROM feedback')
#         feedbacks = cursor.fetchall()

#         # Insert any missing emotions for contacts
#         for email, text in contacts:
#             cursor.execute('SELECT 1 FROM emotions WHERE email=? AND text=?', (email, text))
#             if not cursor.fetchone():
#                 emotion = predict_emotion(text)
#                 cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
#                                (email, text, emotion))
#         # Insert any missing emotions for feedbacks
#         for email, text in feedbacks:
#             cursor.execute('SELECT 1 FROM emotions WHERE email=? AND text=?', (email, text))
#             if not cursor.fetchone():
#                 emotion = predict_emotion(text)
#                 cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
#                                (email, text, emotion))
#         conn.commit()

#         # Fetch all emotions for aggregation
#         cursor.execute('SELECT emotion FROM emotions')
#         rows = cursor.fetchall()

#     all_emotions = ["boredom","anger","empty","enthusiasm","fun","happiness",
#                     "hate","love","neutral","relief","sadness","surprise","worry"]
#     result = {e:0 for e in all_emotions}
#     for r in rows:
#         if r[0] in result:
#             result[r[0]] += 1

#     return jsonify([{"emotion": "All Records", **result}])

# # ------------------- RUN APP -------------------
# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from transformers import pipeline
import hashlib

# ------------------- APP SETUP -------------------
app = Flask(__name__)
CORS(app)
DATABASE = 'contacts.db'

# Load Emotion Model
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

# ------------------- DATABASE INIT -------------------
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                interest TEXT,
                message TEXT
            )
        ''')
        # Registration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS register (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                rating INTEGER,
                comment TEXT,
                emotion TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Emotions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotions (
                email TEXT,
                text TEXT,
                emotion TEXT
            )
        ''')
        conn.commit()

# ------------------- UTILITIES -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def predict_emotion(text):
    if not text or not text.strip():
        return "neutral"
    scores = emotion_classifier(text)[0]
    top_emotion = max(scores, key=lambda x: x['score'])['label'].lower()
    emotion_map = {
        "joy": "happiness", "love": "love", "anger": "anger", "fear": "worry",
        "surprise": "surprise", "sadness": "sadness", "disgust": "hate",
        "neutral": "neutral", "enthusiasm": "enthusiasm", "boredom": "boredom",
        "relief": "relief", "empty": "empty", "fun": "fun", "hate": "hate"
    }
    return emotion_map.get(top_emotion, "neutral")

# ------------------- AUTH ROUTES -------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')
    re_password = data.get('re_password')

    if not all([name, phone, email, password, re_password]):
        return jsonify({'error': 'All fields are required'}), 400
    if password != re_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    hashed_pw = hash_password(password)
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO register (name, phone, email, password)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, hashed_pw))
            conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    hashed_pw = hash_password(password)
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, email, password FROM register WHERE email = ?', (email,))
        row = cursor.fetchone()
        if row and row[2] == hashed_pw:
            return jsonify({'message': 'Login successful', 'name': row[0], 'email': row[1]}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/users', methods=['GET'])
def list_users():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, phone, email, password FROM register')
        users = [{'id': r[0], 'name': r[1], 'phone': r[2], 'email': r[3], 'password': r[4]} for r in cursor.fetchall()]
    return jsonify(users)

# ------------------- CONTACT ROUTES -------------------
@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()
    name, email = data.get('name'), data.get('email')
    interest = data.get('service') or data.get('interest')
    message = data.get('message')

    if not name or not email:
        return jsonify({'error': 'Name and Email are required'}), 400

    emotion = predict_emotion(message)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO contacts (name, email, interest, message) VALUES (?, ?, ?, ?)',
                       (name, email, interest, message))
        cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
                       (email, message, emotion))
        conn.commit()

    return jsonify({'message': 'Contact saved successfully', 'emotion': emotion}), 201

@app.route('/contacts', methods=['GET'])
def list_contacts():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Join contacts with emotions
        cursor.execute('''
            SELECT c.id, c.name, c.email, c.interest, c.message, e.emotion
            FROM contacts c
            LEFT JOIN emotions e ON c.email = e.email AND c.message = e.text
        ''')
        rows = cursor.fetchall()
    return jsonify([
        {
            'id': r[0],
            'name': r[1],
            'email': r[2],
            'interest': r[3],
            'message': r[4],
            'emotion': r[5] or 'neutral'
        }
        for r in rows
    ])

# ------------------- FEEDBACK ROUTES -------------------
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not all([name, email, rating]):
        return jsonify({'error': 'Name, email, and rating are required'}), 400

    emotion = predict_emotion(comment)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedback (name, email, rating, comment, emotion) VALUES (?, ?, ?, ?, ?)',
                       (name, email, rating, comment, emotion))
        cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
                       (email, comment, emotion))
        conn.commit()

    return jsonify({'message': 'Feedback submitted', 'emotion': emotion}), 201

@app.route('/feedback', methods=['GET'])
def get_feedback():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Join feedback with emotions
        cursor.execute('''
            SELECT f.id, f.name, f.email, f.rating, f.comment, f.submitted_at, e.emotion
            FROM feedback f
            LEFT JOIN emotions e ON f.email = e.email AND f.comment = e.text
            ORDER BY f.submitted_at DESC
        ''')
        rows = cursor.fetchall()
    return jsonify([
        {
            'id': r[0],
            'name': r[1],
            'email': r[2],
            'rating': r[3],
            'comment': r[4],
            'submitted_at': r[5],
            'emotion': r[6] or 'neutral'
        }
        for r in rows
    ])

# ------------------- COMBINED RECORDS API -------------------
@app.route('/records', methods=['GET'])
def get_combined_records():
    """Combine contact messages and feedback comments into one emotion count"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Fetch contact messages
        cursor.execute('SELECT email, message FROM contacts')
        contacts = cursor.fetchall()
        # Fetch feedback comments
        cursor.execute('SELECT email, comment FROM feedback')
        feedbacks = cursor.fetchall()

        # Insert any missing emotions for contacts
        for email, text in contacts:
            cursor.execute('SELECT 1 FROM emotions WHERE email=? AND text=?', (email, text))
            if not cursor.fetchone():
                emotion = predict_emotion(text)
                cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
                               (email, text, emotion))
        # Insert any missing emotions for feedbacks
        for email, text in feedbacks:
            cursor.execute('SELECT 1 FROM emotions WHERE email=? AND text=?', (email, text))
            if not cursor.fetchone():
                emotion = predict_emotion(text)
                cursor.execute('INSERT INTO emotions (email, text, emotion) VALUES (?, ?, ?)',
                               (email, text, emotion))
        conn.commit()

        # Fetch all emotions for aggregation
        cursor.execute('SELECT emotion FROM emotions')
        rows = cursor.fetchall()

    all_emotions = ["boredom","anger","empty","enthusiasm","fun","happiness",
                    "hate","love","neutral","relief","sadness","surprise","worry"]
    result = {e:0 for e in all_emotions}
    for r in rows:
        if r[0] in result:
            result[r[0]] += 1

    return jsonify([{"emotion": "All Records", **result}])

# ------------------- COMBINED EMOTION COUNT -------------------
@app.route('/combined-emotion-count', methods=['GET'])
def combined_emotion_count():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT emotion, COUNT(*) AS count
            FROM (
                SELECT emotion FROM emotions
                UNION ALL
                SELECT emotion FROM feedback
            ) AS combined
            GROUP BY emotion
            ORDER BY count DESC
        ''')
        rows = cursor.fetchall()
    return jsonify([{'emotion': r[0], 'count': r[1]} for r in rows])

# ------------------- RUN APP -------------------
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT
    init_db()
    app.run(host='0.0.0.0', port=port, debug=False)

