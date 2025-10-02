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
    return jsonify({"success": True})

# ---------------- Tarefas ----------------
@app.route('/tasks', methods=['GET'])
def list_tasks():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id necessário"}), 400
    db = get_db()
    cur = db.execute('SELECT * FROM tasks WHERE user_id=?', (user_id,))
    tasks = [dict(row) for row in cur.fetchall()]
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    db = get_db()
    db.execute('INSERT INTO tasks (user_id, title, description, status, due_date) VALUES (?, ?, ?, ?, ?)',
               (data['user_id'], data['title'], data.get('description', ''),
                data.get('status', 'todo'), data.get('due_date')))
    db.commit()
    return jsonify({"success": True}), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    db = get_db()
    cur = db.execute('SELECT * FROM tasks WHERE id=?', (task_id,))
    task = cur.fetchone()
    if task:
        return jsonify(dict(task))
    return jsonify({"error":"Task not found"}), 404

@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.json
    db = get_db()
    keys = ['title','description','status','due_date']
    updates = [f"{k} = ?" for k in keys if k in data]
    if not updates:
        return jsonify({"error":"Nada para atualizar"}), 400
    values = [data[k] for k in keys if k in data]
    values.append(task_id)
    db.execute(f'UPDATE tasks SET {", ".join(updates)} WHERE id=?', values)
    db.commit()
    return jsonify({"success": True})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    db.commit()
    return '', 204

# ---------------- Executar ----------------
if __name__ == '__main__':
    app.run(debug=True)