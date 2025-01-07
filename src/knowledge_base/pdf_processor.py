from PyPDF2 import PdfReader
import chromadb
import os
from typing import List, Dict
import nltk
from nltk.tokenize import sent_tokenize
import logging

# Descarga recursos necesarios de NLTK
nltk.download('punkt')

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        # Crear una colección para cada dominio
        self.collections = {
            "medical": self.chroma_client.create_collection("medical_knowledge"),
            "botanical": self.chroma_client.create_collection("botanical_knowledge"),
            "chemical": self.chroma_client.create_collection("chemical_knowledge"),
            "physical": self.chroma_client.create_collection("physical_knowledge"),
            "biological": self.chroma_client.create_collection("biological_knowledge")
        }

    def process_pdf(self, pdf_path: str, domain: str) -> bool:
        """
        Procesa un PDF y lo almacena en la base de datos vectorial.
        
        Args:
            pdf_path: Ruta al archivo PDF
            domain: Dominio al que pertenece (medical, botanical, etc.)
        """
        try:
            # Extraer texto del PDF
            text = self._extract_text(pdf_path)
            
            # Dividir en chunks manejables
            chunks = self._split_into_chunks(text)
            
            # Generar IDs únicos para cada chunk
            doc_ids = [f"{os.path.basename(pdf_path)}_{i}" for i in range(len(chunks))]
            
            # Almacenar en la base vectorial
            self.collections[domain].add(
                documents=chunks,
                ids=doc_ids,
                metadatas=[{"source": pdf_path, "domain": domain} for _ in chunks]
            )
            
            logger.info(f"PDF procesado exitosamente: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando PDF {pdf_path}: {str(e)}")
            return False

    def _extract_text(self, pdf_path: str) -> str:
        """Extrae el texto de un PDF."""
        text = ""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extrayendo texto de {pdf_path}: {str(e)}")
            raise

    def _split_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Divide el texto en chunks más pequeños usando oraciones completas.
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def query_knowledge(self, query: str, domain: str, n_results: int = 5) -> List[Dict]:
        """
        Consulta la base de conocimiento.
        
        Args:
            query: Texto de la consulta
            domain: Dominio a consultar
            n_results: Número de resultados a retornar
        """
        try:
            results = self.collections[domain].query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error consultando la base de conocimiento: {str(e)}")
            return []

# Ejemplo de uso
if __name__ == "__main__":
    processor = PDFProcessor()
    
    # Procesar PDFs de cada dominio
    domains = ["medical", "botanical", "chemical", "physical", "biological"]
    for domain in domains:
        pdf_dir = f"src/knowledge_base/{domain}"
        for pdf_file in os.listdir(pdf_dir):
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(pdf_dir, pdf_file)
                processor.process_pdf(pdf_path, domain)