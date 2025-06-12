from main import db
from services.dateformat import now_paris

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=now_paris)

    faqs = db.relationship('FAQ', backref='document', lazy=True)

    def __repr__(self):
        return f"<Document {self.filename}>"