from models.document import Document
from models.faq import FAQ
from services.ragengine import RagEngine
from database.instance import db, app
from flask import render_template
import os

@app.route("/")
def home():
    faqs = FAQ.query.filter_by(document_id=1).order_by(FAQ.number).limit(10).all()
    return render_template('base.html', faqs=faqs)


if __name__ == '__main__':
    app.run(debug=True, port=5001)