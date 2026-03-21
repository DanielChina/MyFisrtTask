from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import date, timedelta
import json
import os

USERS_FILE = "users.json"


def get_CSV_data(source_path):
    with open(source_path) as csv_file:
        return csv_file.read()


stu_info = get_CSV_data("data/stu.csv")
teacher_info = get_CSV_data("data/teacher.csv")


def ensure_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def load_users():
    ensure_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def find_user(username):
    users = load_users()
    for user in users:
        if user["username"].lower() == username.lower():
            return user
    return None


def is_logged_in():
    return session.get("user_logged_in", False)


def dashboard():
    if not is_logged_in():
        return redirect(url_for("auth"))

    days = 10
    start = date.today() - timedelta(days=days - 1)

    labels = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    values = [random.randint(10, 90) for _ in range(days)]

    kpi_total = sum(values)
    kpi_avg = round(kpi_total / len(values), 1)
    kpi_max = max(values)

    rows = []
    for i in range(days - 1, -1, -1):
        v = values[i]
        status = "OK" if v < 70 else "High"
        note = "Within normal range" if status == "OK" else "Review recommended"

        rows.append({
            "date": labels[i],
            "value": v,
            "status": status,
            "note": note
        })

    return render_template(
        "dashboard.jinja2",
        labels=labels,
        values=values,
        kpi_total=kpi_total,
        kpi_avg=kpi_avg,
        kpi_max=kpi_max,
        rows=rows
    )


def auth():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action", "").strip()

        if action == "register":
            username = request.form.get("register_username", "").strip()
            password = request.form.get("register_password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            if not username or not password or not confirm_password:
                flash("All register fields are required.", "danger")
                return render_template("auth.jinja2", active_tab="register")

            if len(username) < 3:
                flash("Username must be at least 3 characters.", "danger")
                return render_template("auth.jinja2", active_tab="register")

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("auth.jinja2", active_tab="register")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("auth.jinja2", active_tab="register")

            if find_user(username):
                flash("Username already exists.", "danger")
                return render_template("auth.jinja2", active_tab="register")

            users = load_users()
            users.append({
                "username": username,
                "password_hash": generate_password_hash(password)
            })
            save_users(users)

            flash("Registration successful. Please log in.", "success")
            return render_template("auth.jinja2", active_tab="login")

        elif action == "login":
            username = request.form.get("login_username", "").strip()
            password = request.form.get("login_password", "").strip()

            if not username or not password:
                flash("Username and password are required.", "danger")
                return render_template("auth.jinja2", active_tab="login")

            user = find_user(username)
            if user and check_password_hash(user["password_hash"], password):
                session["user_logged_in"] = True
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))

            flash("Invalid username or password.", "danger")
            return render_template("auth.jinja2", active_tab="login")

    return render_template("auth.jinja2", active_tab="login")


def logout():
    session.clear()
    return redirect(url_for("auth"))


def init_app(app):
    app.add_url_rule("/", "dashboard", dashboard)
    app.add_url_rule("/auth", "auth", auth, methods=["GET", "POST"])
    app.add_url_rule("/logout", "logout", logout)

import csv

def is_valid_student(row):
    try:
        student_id = int(row["ID"])
        age = int(row["Age"])
        name = row["Name"].strip()
        gender = row["Gender"].strip()
        grade = row["Grade"].strip()

        if age < 1 or age > 120:
            return False, "Invalid age"

        if not name:
            return False, "Empty name"

        if gender not in ["Male", "Female"]:
            return False, "Invalid gender"

        if grade not in ["A", "B", "C", "D", "E", "F"]:
            return False, "Invalid grade"

        return True, {
            "ID": student_id,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Grade": grade
        }

    except ValueError:
        return False, "ID or Age is not a valid integer"

valid_students = []
invalid_rows = []

with open("students.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for line_num, row in enumerate(reader, start=2):
        ok, result = is_valid_student(row)
        if ok:
            valid_students.append(result)
        else:
            invalid_rows.append((line_num, row, result))

print("Valid students:")
for s in valid_students:
    print(s)

print("\nInvalid rows:")
for line_num, row, reason in invalid_rows:
    print(f"Line {line_num}: {row} -> {reason}")