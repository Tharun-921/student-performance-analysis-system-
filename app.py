
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, FuelRecord

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fuel-analysis-secret-key")

# Database configuration
database_url = os.environ.get("DATABASE_URL", "sqlite:///fuel.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    records = FuelRecord.query.order_by(FuelRecord.id.desc()).all()

    total_litres = sum(record.litres for record in records)
    total_cost = sum(record.total_cost for record in records)

    return render_template(
        "dashboard.html",
        records=records,
        total_litres=round(total_litres, 2),
        total_cost=round(total_cost, 2),
        total_records=len(records)
    )


@app.route("/fuel/add", methods=["POST"])
def add_fuel():
    try:
        record = FuelRecord(
            vehicle_number=request.form["vehicle_number"].strip(),
            date=__import__("datetime").date.fromisoformat(request.form["date"]),
            fuel_type=request.form["fuel_type"],
            litres=float(request.form["litres"]),
            price_per_litre=float(request.form["price_per_litre"]),
            odometer=float(request.form["odometer"])
        )

        if (
            not record.vehicle_number
            or record.litres <= 0
            or record.price_per_litre <= 0
            or record.odometer < 0
        ):
            flash("Please enter valid fuel details.", "error")
            return redirect(url_for("dashboard"))

        db.session.add(record)
        db.session.commit()
        flash("Fuel record added successfully!", "success")

    except (ValueError, KeyError):
        db.session.rollback()
        flash("Invalid details. Please check your inputs.", "error")

    return redirect(url_for("dashboard"))


@app.route("/fuel/delete/<int:record_id>", methods=["POST"])
def delete_fuel(record_id):
    record = db.session.get(FuelRecord, record_id)

    if record:
        db.session.delete(record)
        db.session.commit()
        flash("Fuel record deleted.", "success")

    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return {"status": "ok"}, 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
