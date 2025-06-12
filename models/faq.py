from main import db
from services.dateformat import now_paris

class FAQ(db.Model):
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    number = db.Column(db.Integer, nullable=False) # de 1 à 10 pour les questions/réponses d'une FAQ
    updated_at = db.Column(db.DateTime, default=now_paris, onupdate=now_paris)

    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)

    def __repr__(self):
        return f"<FAQ {self.id}>"