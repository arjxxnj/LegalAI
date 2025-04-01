from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cases = db.relationship('Case', backref='client', lazy=True)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_type = db.Column(db.String(100), nullable=False)
    offense_description = db.Column(db.Text, nullable=False)
    incident_date = db.Column(db.Date, nullable=True)
    incident_location = db.Column(db.String(200), nullable=True)
    victim_details = db.Column(db.Text, nullable=True)
    accused_details = db.Column(db.Text, nullable=True)
    evidence_summary = db.Column(db.Text, nullable=True)
    query = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ipc_sections = db.Column(db.Text, nullable=True)  # Stored as comma-separated IDs
    analysis = db.Column(db.Text, nullable=True)
    relevant_precedents = db.Column(db.Text, nullable=True)  # Stored as comma-separated IDs
