from models.document import Document
from models.faq import FAQ
from services.ragengine import RagEngine
from database.instance import db, app
from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
import os
from threading import Thread

app.config['UPLOAD_FOLDER'] = os.path.abspath('./data')

@app.route("/")
def home():
    return render_template('base.html')

@app.route("/faq", methods=["GET", "POST"])
def showfaq():
    document_id = request.args.get('document_id', type=int, default=3)
    document = Document.query.get(document_id)
    if not document:
        flash(f"Document avec l'id {document_id} non trouvé.")
        return render_template('faq.html', faqs=[], document=None)

    
    if request.method == "POST":
        # Lancer la génération en arrière-plan
        def generate_faqs(document):
            rag = RagEngine()
            rag.init_llm("llama3.2:1b")
            rag.process_and_save_faqs(
                document=document,
                num_faqs=10,
                chunk_size=500,
                overlap=50
            )

        Thread(target=generate_faqs, args=(document,), daemon=True).start()
        flash("Génération des FAQ en cours... Veuillez recharger la page dans quelques instants.")

        # On retourne les anciennes FAQ (ou vide)
        faqs = FAQ.query.filter_by(document_id=document_id).order_by(FAQ.number).limit(10).all()
    else:
        # GET : juste récupérer les FAQ existantes
        faqs = FAQ.query.filter_by(document_id=document_id).order_by(FAQ.number).limit(10).all()

    return render_template('faq.html', faqs=faqs, document=document)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier trouvé dans la requête.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)

        if file:
            extension = os.path.splitext(file.filename)[1]
            unique_name = f"{uuid.uuid4().hex}{extension}"
            filename = secure_filename(unique_name)

            # Chemin absolu pour sauvegarder physiquement le fichier
            abs_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(abs_path)

            # Chemin relatif à stocker en base, calculé à partir du dossier courant
            rel_path = '.' + os.sep + os.path.relpath(abs_path, start=os.getcwd())

            # Ajout en base de données
            with app.app_context():
                document = Document.query.filter_by(filepath=rel_path).first()
                if not document:
                    document = Document(filename=filename, filepath=rel_path)
                    db.session.add(document)
                    db.session.commit()
                    flash(f"Document '{filename}' uploadé et enregistré en base.")
                else:
                    flash(f"Document '{filename}' déjà présent en base.")

            return redirect(url_for('upload_file'))

    return render_template('upload.html')

@app.route('/list')
def list_documents():
    documents = Document.query.order_by(Document.id.desc()).all()
    return render_template('list.html', documents=documents)

if __name__ == '__main__':
    app.run(debug=True, port=5001)