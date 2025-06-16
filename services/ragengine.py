from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from services.documentprocessor import DocumentProcessor
from models.document import Document
from models.faq import FAQ
from database.instance import db

class RagEngine:
    def __init__(self):
        self.llm = None
        self.document_processor = DocumentProcessor()
        
    def init_llm(self, llm_name):
        self.llm = Ollama(model=llm_name)
        print(f"Modèle {llm_name} démarré...")
        return self.llm
    
    def process_document_to_faqs(self, document: Document, num_faqs=10, chunk_size=500, overlap=50):
        if not self.llm:
            raise ValueError("LLM non initialisé. Utilisez init_llm() d'abord.")
        
        print(f"Traitement du document: {document.filename}")
        
        # 1. Extraire le texte du PDF
        text = self.document_processor.extract_text_from_pdf(document)
        print(f"Texte extrait: {len(text)} caractères")
        
        # 2. Créer les chunks
        chunks = self.document_processor.text_to_chunks(text, chunk_size, overlap)
        print(f"Chunks créés: {len(chunks)} chunks")
        
        # 3. Générer les FAQ à partir des chunks
        faqs = self.generate_faqs_from_chunks(chunks, document.id, num_faqs)
        
        return faqs
    
    def generate_faqs_from_chunks(self, chunks, document_id, num_faqs=10):
        if not self.llm:
            raise ValueError("LLM non initialisé. Utilisez init_llm() d'abord.")
        
        # Créer le contexte à partir des chunks
        context = self._create_context_from_chunks(chunks)
        
        # Template pour générer des FAQ
        faq_template = PromptTemplate(
            input_variables=["context", "num_faqs"],
            template="""Analysez le document suivant et générez {num_faqs} questions-réponses (FAQ) pertinentes.

Contexte du document:
{context}

Instructions:
- Créez exactement {num_faqs} questions-réponses
- Les questions doivent être claires et pratiques
- Les réponses doivent être basées uniquement sur le contenu fourni
- Numérotez chaque FAQ de 1 à {num_faqs}
- Format requis:
  Q1: [Question]
  R1: [Réponse]
  Q2: [Question]
  R2: [Réponse]
  ... etc
- Format json permettant ensuite de modifier une Q/R

FAQ:"""
        )
        
        print(f"Génération de {num_faqs} FAQ...")
        
        # Générer les FAQ avec le LLM
        sequence = faq_template | self.llm
        response = sequence.invoke({
            "context": context,
            "num_faqs": min(num_faqs, 10)  # Limiter à 10 max
        })
        
        # Parser la réponse et créer les objets FAQ
        faqs = self._parse_faq_response(response, document_id)
        
        print(f"{len(faqs)} FAQ générées")
        return faqs
    
    def _create_context_from_chunks(self, chunks, max_chars=4000):
        """Crée un contexte condensé à partir des chunks du DocumentProcessor"""
        context_parts = []
        current_length = 0
        
        for i, chunk in enumerate(chunks):
            # Nettoyer le chunk (supprimer les espaces multiples)
            clean_chunk = ' '.join(chunk.split())
            
            # Vérifier si on dépasse la limite
            if current_length + len(clean_chunk) > max_chars:
                break
                
            context_parts.append(f"Section {i+1}: {clean_chunk}")
            current_length += len(clean_chunk)
        
        return "\n\n".join(context_parts)
    
    def _parse_faq_response(self, response, document_id):
        """Parse la réponse du LLM pour extraire les questions/réponses"""
        faqs = []
        lines = response.split('\n')
        
        current_question = None
        current_answer = None
        current_number = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Détecter une question (Q1:, Q2:, etc.)
            if line.startswith('Q') and ':' in line:
                # Sauvegarder la FAQ précédente si elle existe
                if current_question and current_answer:
                    faq = FAQ(
                        question=current_question,
                        answer=current_answer,
                        number=current_number,
                        document_id=document_id
                    )
                    faqs.append(faq)
                
                # Extraire le numéro et la question
                try:
                    parts = line.split(':', 1)
                    current_number = int(''.join(filter(str.isdigit, parts[0])))
                    current_question = parts[1].strip() if len(parts) > 1 else ""
                    current_answer = None
                except ValueError:
                    continue
            
            # Détecter une réponse (R1:, R2:, etc.)
            elif line.startswith('R') and ':' in line and current_question:
                parts = line.split(':', 1)
                current_answer = parts[1].strip() if len(parts) > 1 else ""
            
            # Continuer une réponse sur plusieurs lignes
            elif current_answer is not None and not line.startswith(('Q', 'R')):
                current_answer += " " + line
        
        # Ajouter la dernière FAQ
        if current_question and current_answer:
            faq = FAQ(
                question=current_question,
                answer=current_answer,
                number=current_number,
                document_id=document_id
            )
            faqs.append(faq)
        
        return faqs
    
    def save_faqs_to_database(self, faqs):
        """Sauvegarde les FAQ en base de données"""
        try:
            for faq in faqs:
                db.session.add(faq)
            db.session.commit()
            print(f"{len(faqs)} FAQ sauvegardées en base de données")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def process_and_save_faqs(self, document: Document, num_faqs=10, chunk_size=500, overlap=50):
        """
        Pipeline complet avec sauvegarde automatique
        
        Args:
            document: Objet Document de la base de données
            num_faqs: Nombre de FAQ à générer
            chunk_size: Taille des chunks pour le DocumentProcessor
            overlap: Chevauchement entre chunks
        
        Returns:
            Liste d'objets FAQ sauvegardés
        """
        # Générer les FAQ
        faqs = self.process_document_to_faqs(document, num_faqs, chunk_size, overlap)
        
        # Sauvegarder en base
        if faqs:
            success = self.save_faqs_to_database(faqs)
            if success:
                return faqs
            else:
                return []
        
        return []
