import logging
from typing import List, Dict, Optional
import numpy as np
from src.rag.vector_store.vector_db import VectorDB

logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self):
        self.vector_db = VectorDB()

    def retrieve_documents(
        self,
        query: str,
        domain: str,
        n_results: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Recupera documentos relevantes para una consulta.
        """
        try:
            if domain not in self.vector_db.collections:
                raise ValueError(f"Dominio no válido: {domain}")

            results = self.vector_db.search(
                query=query,
                domain=domain,
                n_results=n_results
            )

            # Procesamos los resultados
            documents = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"],
                results["metadatas"],
                results["distances"]
            )):
                # Convertir distancia a similitud
                similarity = 1 - (distance / np.sqrt(2))
                
                if similarity >= similarity_threshold:
                    documents.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': float(similarity),
                        'rank': i + 1
                    })

            return documents

        except Exception as e:
            logger.error(f"Error recuperando documentos: {str(e)}")
            raise

    def retrieve_multi_domain(
        self,
        query: str,
        domains: Optional[List[str]] = None,
        n_results: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Recupera documentos de múltiples dominios.
        """
        if domains is None:
            domains = list(self.vector_db.collections.keys())

        results = {}
        for domain in domains:
            try:
                domain_docs = self.retrieve_documents(
                    query=query,
                    domain=domain,
                    n_results=n_results
                )
                results[domain] = domain_docs
            except Exception as e:
                logger.error(f"Error en dominio {domain}: {str(e)}")
                results[domain] = []

        return results

    def get_document_by_id(self, document_id: str, domain: str) -> Optional[Dict]:
        """
        Recupera un documento específico por su ID.
        """
        try:
            if domain not in self.vector_db.collections:
                raise ValueError(f"Dominio no válido: {domain}")

            result = self.vector_db.get_collection_stats(domain)
            
            if result:
                return {
                    'content': result['documents'][0] if result['documents'] else None,
                    'metadata': result['metadatas'][0] if result['metadatas'] else {}
                }
            return None

        except Exception as e:
            logger.error(f"Error recuperando documento {document_id}: {str(e)}")
            return None