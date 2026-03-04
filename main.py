from flask import Flask, render_template
import random
from datetime import date, timedelta

app = Flask(__name__)

@app.route("/")
def dashboard():

    days = 10
    start = date.today() - timedelta(days=days-1)

    labels = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    values = [random.randint(10, 90) for _ in range(days)]

    kpi_total = sum(values)
    kpi_avg = round(kpi_total / len(values), 1)
    kpi_max = max(values)

    rows = []
    for i in range(days-1, -1, -1):

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


if __name__ == "__main__":
    app.run(debug=True)