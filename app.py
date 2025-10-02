from flask import Flask, request, jsonify, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = 'tasks.db'

# ---------------- Conexão com SQLite ----------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------------- Rotas Front-end ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- Usuários ----------------
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    db = get_db()
    try:
        db.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                   (data['email'], data['password']))
        db.commit()
        return jsonify({"success": True}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email já existe"}), 400

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    cur = db.execute('SELECT id, email FROM users WHERE id=?', (user_id,))
    user = cur.fetchone()
    if user:
        return jsonify(dict(user))
    return jsonify({"error": "Usuário não encontrado"}), 404

# ---------------- Sessão ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE email=? AND password=?',
                     (data['email'], data['password']))
    user = cur.fetchone()
    if user:
        return jsonify({"success": True, "user_id": user["id"]})
    return jsonify({"success": False}), 401

@app.route('/logout', methods=['POST'])
def logout():
    # Apenas placeholder (RESTful) para API stateless
    return jsonify({"success": True})
