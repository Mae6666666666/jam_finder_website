import os

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder="template")


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="bandfinder_user",
        password=os.environ.get("DB_PASSWORD", ""),
        database="bandfinder_db",
    )


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def post_login():
    username = request.form["username"].strip()
    password = request.form["password"]

    if not username or len(password) < 8:
        return render_template("login.html", error="Invalid username or password. Password need at least 8 characters.")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT username, password_hash FROM users WHERE username = %s", (username,)
        )
        user = cursor.fetchone()
        if user is None:
            return render_template("login.html", error="Username does not exist")

        db_username, db_password = user
        if check_password_hash(db_password, password):
            print("login success")
            return render_template("homepage.html")
        else:
            print("login fail")
            return render_template("login.html", error="Password is incorrect, try again")

    except:
        return render_template("login.html", error="Failed to load")

    finally:
        cursor.close()
        db.close()


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        username = request.form["username"].strip()
        password = request.form["password"]

        if not email or not username or len(password) < 8:
            return render_template("signup.html", error="Fill in every box. Passwords need at least 8 characters.")

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (email, username, password_hash) VALUES (%s, %s, %s)",
                (email, username, generate_password_hash(password)),
            )
            db.commit()
        except mysql.connector.IntegrityError:
            return render_template("signup.html", error="That email or username is already taken.")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)