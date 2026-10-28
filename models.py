
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FuelRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    fuel_type = db.Column(db.String(30), nullable=False)
    litres = db.Column(db.Float, nullable=False)
    price_per_litre = db.Column(db.Float, nullable=False)
    odometer = db.Column(db.Float, nullable=False)

    @property
    def total_cost(self):
        return round(self.litres * self.price_per_litre, 2)
