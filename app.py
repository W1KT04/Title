from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Create database if it doesn't exist
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        text TEXT
    )""")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    comments = {}
    for post in posts:
        c.execute("SELECT * FROM comments WHERE post_id=?", (post[0],))
        comments[post[0]] = c.fetchall()
    conn.close()
    return render_template("index.html", posts=posts, comments=comments)

@app.route("/add_post", methods=["POST"])
def add_post():
    password = request.form.get("password")
    if password != "admin123":
        return "Unauthorized", 403
    title = request.form.get("title")
    content = request.form.get("content")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/add_comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    text = request.form.get("comment")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO comments (post_id, text) VALUES (?, ?)", (post_id, text))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")
    if password == "Blender650g":
        session['admin'] = True
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect("/")

@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM comments WHERE post_id=?", (post_id,))
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    if not session.get('admin'):
        return "Unauthorized", 403
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)