from models.document import Document
from services.ragengine import RagEngine
from database.instance import db, app
import os

def example_usage():
    with app.app_context():
        # Définir le chemin du fichier PDF
        pdf_path = "./data/document3.pdf"
        pdf_name = os.path.basename(pdf_path)
        document = Document.query.filter_by(filepath=pdf_path).first()
        if not document:
            # Ajouter le document à la base
            document = Document(filename=pdf_name, filepath=pdf_path)
            db.session.add(document)
            db.session.commit()
            print(f"Document '{pdf_name}' ajouté à la base.")
        else:
            print(f"Document '{pdf_name}' déjà présent dans la base.")

        document = Document.query.filter_by(filepath=pdf_path).first()
        
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