from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "replace-with-a-strong-secret-key"


def is_logged_in():
    return session.get("user_logged_in", False)


@app.route("/")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

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


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Simple demo only
        if username == "admin" and password == "123456":
            session["user_logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.jinja2")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)