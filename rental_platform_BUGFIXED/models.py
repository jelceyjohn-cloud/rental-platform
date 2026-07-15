"""
models.py — Database layer (SQLite via SQLAlchemy)

Three tables, one relationship:
  Property  <---- (one-to-many) ----  Application
  Admin (separate, for dashboard login)
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))
    price = db.Column(db.Integer, nullable=False)          # monthly rent
    bedrooms = db.Column(db.Integer, default=1)
    bathrooms = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # This lets us write property.applications to get every application
    # submitted for this specific property (SQLAlchemy relationship).
    applications = db.relationship(
        'Application', backref='property', cascade='all, delete-orphan'
    )


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key -> links this application to one Property row
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)

    applicant_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    move_in_date = db.Column(db.String(20), nullable=False)
    occupants = db.Column(db.Integer, default=1)
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
