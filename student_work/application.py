# Your code will go here
from flask import Flask, request, redirect, url_for, render_template_string, session
import sqlite3
import bcrypt
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- DATABASE SETUP ----------
def is_valid_password(password):
    if (re.search(r"[A-Z]", password) and   # uppercase
        re.search(r"[a-z]", password) and   # lowercase
        re.search(r"[0-9]", password) and   # number
        re.search(r"[^A-Za-z0-9]", password)):  # special char
        return True
    return False

def get_db(name_of_the_base):
    conn = sqlite3.connect(f"{name_of_the_base}.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(name_of_the_base):
    conn = get_db(name_of_the_base)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db('users')
init_db('writings')

# ---------- STYLE ----------
base_style = """
<style>
body {
    font-family: Arial, sans-serif;
    background: #ffc7fc;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(192, 31, 171, 0.4);
    width: 300px;
    text-align: center;
}
input {
    width: 90%;
    padding: 8px;
    margin: 8px 0;
}
button {
    padding: 10px;
    width: 60%;
    background: #fffb08;
    color: black;
    border: none;
}
.error {
    color: red;
}
</style>
"""

login_page = f"""{base_style}
<div class="card">
<h2>Login</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Login</button>
</form>
<a href="/register">Create an account</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

register_page = f"""{base_style}
<div class="card">
<h2>Register</h2>
<form method="POST">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Sign Up</button>
</form>
<a href="/">Back to login</a>
<p class="error">{{{{ error }}}}</p>
</div>
"""

secret_style = """
<style>
body {
    font-family: Arial, sans-serif;
    background: #ffc7fc;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(192, 31, 171, 0.4);
    width: 300px;
    text-align: center;
}
input {
    width: 90%;
    padding: 8px;
    margin: 8px 0;
}
button {
    padding: 10px;
    width: 60%;
    background: #fffb08;
    color: black;
    border: none;
}
.error {
    color: red;
}
</style>
"""

secret_page = f"""{secret_style}
<div class="card">
<h2>💖🔑Unlocked🔑💖</h2>
<h3>Welcome, {{{{ username }}}},</h3>
<p>to MyPrivateLife!</p>
<a href="/logout"><button>logout</button></a>
<form method="POST">
  <input name="entry of choice"><br>
  <button type="submit">Which entry?</button>
</form>
</div>
"""

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db('users')
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        # user['password'] is bytes in SQLite; check with bcrypt
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user"] = username
            return redirect(url_for("secret"))
        else:
            error = "Incorrect username or password"

    return render_template_string(login_page, error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            error = "Fields cannot be empty"
        elif not is_valid_password(password):
            error = "Password must include uppercase, lowercase, number, and special character"
        else:
            conn = get_db('users')
            try:
                # Hash password with bcrypt
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()

                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                conn.rollback()
                error = "Username already exists"
            except Exception:
                conn.rollback()
                error = "Unexpected error during registration"
            finally:
                conn.close()

    return render_template_string(register_page, error=error)

@app.route("/secret")
# TODO make link for entries in here plus updating writings database
def secret():
    if "user" not in session:
        return redirect(url_for("login"))
    # if request.method == "POST":
    #     return redirect(url_for(""))

    return render_template_string(secret_page, username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
app.run(host="0.0.0.0", port=5000)