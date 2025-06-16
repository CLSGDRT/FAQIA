from models.document import Document
import PyPDF2

class DocumentProcessor:
    def __init__(self):
        pass

    @staticmethod
    def extract_text_from_pdf(document: Document):
        with open(document.filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                try:
                    text += page.extract_text() or ""
                except Exception as e:
                    print(f"Erreur d'extraction sur une page : {e}")
        return text
    
    @staticmethod
    def text_to_chunks(text, chunk_size=500, overlap=50): # Découpe du texte en chunk pour permettre au modèle d'être plus précis
        chunks = []
        i = 0
        while i < len(text):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
            i += chunk_size - overlap  # on décale en conservant le chevauchement
        return chunks