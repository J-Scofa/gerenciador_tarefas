from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "segredo"  # necessário para sessões

DATABASE = "tasks.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------
# ROTAS DE AUTENTICAÇÃO
# ---------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        else:
            return "Login inválido!"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        db.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------------
# ROTAS DE TAREFAS
# ---------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))  # só acessa se estiver logado
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],)).fetchall()
    return render_template("index.html", tasks=tasks)

@app.route("/tasks", methods=["POST"])
def create_task():
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form["title"]
    db = get_db()
    db.execute("INSERT INTO tasks (user_id, title, status) VALUES (?, ?, ?)", (session["user_id"], title, "todo"))
    db.commit()
    return redirect(url_for("index"))

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, session["user_id"]))
    db.commit()
    return redirect(url_for("index"))

@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, session["user_id"])).fetchone()
    if task:
        new_status = "done" if task["status"] == "todo" else "todo"
        db.execute("UPDATE tasks SET status=? WHERE id=? AND user_id=?", (new_status, task_id, session["user_id"]))
        db.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)