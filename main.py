from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.document import Document
from services.ragengine import RagEngine


app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/easyy/Developpement/Python/FAQIA/database/faqia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def example_usage():
    """Exemple d'utilisation avec vos classes"""
    
    # Supposons que vous ayez un document en base de données
    document = Document.query.first()  # ou Document.query.get(document_id)
    
    if not document:
        print("Aucun document trouvé en base")
        return
    
    # Initialiser le RAG Engine
    rag = RagEngine()
    rag.init_llm("llama3")
    
    # Méthode 1: Pipeline complet avec sauvegarde automatique
    faqs = rag.process_and_save_faqs(
        document=document,
        num_faqs=10,
        chunk_size=500,
        overlap=50
    )
    
    # Afficher les FAQ générées
    for faq in faqs:
        print(f"FAQ {faq.number} (Document: {faq.document_id}):")
        print(f"Q: {faq.question}")
        print(f"R: {faq.answer}")
        print(f"Mis à jour: {faq.updated_at}")
        print("-" * 60)
    
    # Méthode 2: Si vous voulez seulement générer sans sauvegarder
    # faqs = rag.process_document_to_faqs(document, num_faqs=5)
    
    # Méthode 3: Si vous avez déjà des chunks
    # chunks = rag.document_processor.text_to_chunks(texte)
    # faqs = rag.generate_faqs_from_chunks(chunks, document.id)

if __name__ == "__main__":
    example_usage()