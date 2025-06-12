import PyPDF2

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from services.documentprocessor import DocumentProcessor


class RagEngine:
    def __init__(self):
        pass

        def init_llm(self, llm_name):
            ollama = Ollama(model=llm_name)
            print(f"Modèle {llm_name} démarré...")
        
        def load_chunks(chunks: DocumentProcessor):
            return 0


# Initialiser Ollama
# ollama = Ollama(model="llama3")

promptInput = input("Entrez le texte du prompt: ")
promptText = promptInput+"\n\n{text}\n\nAnswer:"

prompt_template = PromptTemplate(
    input_variables=["text"],
    template=promptText
)
# chunks = chunk_text(pdf_text, chunk_size=1000)

# Utiliser le pipe (|) pour combiner le prompt et le LLM
sequence = prompt_template | ollama


#récupérer les réponses sans chunk
# response = sequence.invoke({"text": pdf_text})
# print(f"Response: {response}")

# Diviser le texte en chunks
# chunks = chunk_text(pdf_text, chunk_size=1000)

# # Traiter chaque chunk et récupérer les réponses
# for i, chunk in enumerate(chunks):
#     print(f"Processing chunk {i+1}/{len(chunks)}...")
#     response = sequence.invoke({"text": chunk})
#     print(f"Chunk {i+1} response: {response}")



# # Traiter chaque chunk et récupérer les réponses
# for i, chunk in enumerate(chunks):
#     print(f"Processing chunk {i+1}/{len(chunks)}...")
#     response = sequence.invoke({"text": chunk})
#     print(f"Chunk {i+1} response: {response}")

    