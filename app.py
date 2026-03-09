from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import (init_db, get_all_habits, add_habit, delete_habit,
                      mark_complete, unmark_complete, get_completions,
                      get_stats, create_user, verify_password, get_user_by_id)
from datetime import date, timedelta
from functools import wraps

app = Flask(__name__)
import os
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    habits = get_all_habits(user_id)
    today = date.today().isoformat()
    habit_data = []
    for habit in habits:
        completions = get_completions(habit["id"])
        stats = get_stats(habit["id"])
        last_21 = [
            (date.today() - timedelta(days=i)).isoformat()
            for i in range(20, -1, -1)
        ]
        heatmap = [{"date": d, "done": d in completions} for d in last_21]
        habit_data.append({
            "id": habit["id"],
            "name": habit["name"],
            "done_today": today in completions,
            "streak": stats["streak"],
            "total": stats["total"],
            "weekly_percentage": stats["weekly_percentage"],
            "heatmap": heatmap
        })
    username = get_user_by_id(user_id)["username"]
    return render_template("index.html", habits=habit_data, today=today, username=username)

@app.route("/add", methods=["POST"])
@login_required
def add():
    name = request.form.get("name", "").strip()
    if name:
        add_habit(session["user_id"], name)
    return redirect(url_for("index"))

@app.route("/toggle/<int:habit_id>", methods=["POST"])
@login_required
def toggle(habit_id):
    today = date.today().isoformat()
    completions = get_completions(habit_id)
    if today in completions:
        unmark_complete(habit_id)
    else:
        mark_complete(habit_id)
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
@login_required
def delete(habit_id):
    delete_habit(habit_id, session["user_id"])
    return redirect(url_for("index"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("signup"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("signup"))
        if create_user(username, password):
            flash("Account created! Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Username already taken.")
            return redirect(url_for("signup"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = verify_password(username, password)
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
