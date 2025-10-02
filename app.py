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