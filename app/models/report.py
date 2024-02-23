# app/models/report.py
from app.extensions import db
from datetime import datetime

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_name = db.Column(db.String(100), default="Anonymous")
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False)  # False for "Open", True for "Resolved"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Report {self.id} - {self.reporter_name}>"