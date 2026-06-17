from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from database import get_connection
import os

app = Flask(__name__)
app.secret_key = "todo_secret_key_2024"
CORS(app, supports_credentials=True)


# ─────────────────────────────────────────────
# HTML ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "login.html")

@app.route("/login.html")
def login_page():
    return send_from_directory(".", "login.html")

@app.route("/todo.html")
def todo():
    return send_from_directory(".", "todo.html")


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({"success": True, "message": "Login successful", "username": user["username"], "user_id": user["id"]})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "All fields required"}), 400

    if len(password) < 4:
        return jsonify({"success": False, "message": "Password must be at least 4 characters"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return jsonify({"success": True, "message": "Registered successfully! Please login."})
    except Exception as e:
        return jsonify({"success": False, "message": "Username already exists"}), 409
    finally:
        cursor.close()
        conn.close()


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})


# ─────────────────────────────────────────────
# TODO CRUD ROUTES
# ─────────────────────────────────────────────

@app.route("/api/todos", methods=["GET"])
def get_todos():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "user_id required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    todos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "todos": todos})


@app.route("/api/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not user_id or not title:
        return jsonify({"success": False, "message": "user_id and title required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (user_id, title, description, status) VALUES (%s, %s, %s, 'pending')",
        (user_id, title, description)
    )
    conn.commit()
    todo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Todo created!", "id": todo_id}), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    status = data.get("status", "pending")

    if not title:
        return jsonify({"success": False, "message": "Title required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET title=%s, description=%s, status=%s WHERE id=%s",
        (title, description, status, todo_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Todo updated!"})


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id=%s", (todo_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Todo deleted!"})


@app.route("/api/todos/<int:todo_id>/status", methods=["PATCH"])
def toggle_status(todo_id):
    data = request.get_json()
    status = data.get("status")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET status=%s WHERE id=%s", (status, todo_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Status updated!"})


    if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
