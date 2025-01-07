import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True
        ))
        self.collections = {}
        self._initialize_collections()

    def _initialize_collections(self):
        """Inicializa las colecciones para cada dominio"""
        domains = ["medical", "botanical", "chemical", "physical", "biological"]
        for domain in domains:
            collection_name = f"{domain}_collection"
            try:
                self.collections[domain] = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"domain": domain}
                )
            except Exception as e:
                logger.error(f"Error inicializando colección {collection_name}: {str(e)}")
                raise

    async def add_texts(
        self,
        texts: List[str],
        metadata: List[Dict],
        domain: str,
        ids: Optional[List[str]] = None
    ):
        """
        Añade textos a la colección correspondiente
        """
        try:
            if domain not in self.collections:
                raise ValueError(f"Dominio no válido: {domain}")

            if ids is None:
                ids = [f"doc_{i}" for i in range(len(texts))]

            self.collections[domain].add(
                documents=texts,
                metadatas=metadata,
                ids=ids
            )
            logger.info(f"Añadidos {len(texts)} documentos a la colección {domain}")

        except Exception as e:
            logger.error(f"Error añadiendo textos a {domain}: {str(e)}")
            raise

    async def search(
        self,
        query: str,
        domain: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> Dict:
        """
        Busca documentos similares en la colección
        """
        try:
            if domain not in self.collections:
                raise ValueError(f"Dominio no válido: {domain}")

            results = self.collections[domain].query(
                query_texts=[query],
                n_results=n_results,
                where=metadata_filter
            )

            return {
                "ids": results["ids"][0],
                "documents": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0]
            }

        except Exception as e:
            logger.error(f"Error en búsqueda para {domain}: {str(e)}")
            raise

    async def delete_texts(self, ids: List[str], domain: str):
        """
        Elimina documentos por sus IDs
        """
        try:
            if domain not in self.collections:
                raise ValueError(f"Dominio no válido: {domain}")

            self.collections[domain].delete(ids=ids)
            logger.info(f"Eliminados {len(ids)} documentos de la colección {domain}")

        except Exception as e:
            logger.error(f"Error eliminando documentos de {domain}: {str(e)}")
            raise

    async def get_collection_stats(self, domain: str) -> Dict:
        """
        Obtiene estadísticas de una colección
        """
        try:
            if domain not in self.collections:
                raise ValueError(f"Dominio no válido: {domain}")

            collection = self.collections[domain]
            return {
                "count": collection.count(),
                "domain": domain,
                "name": collection.name
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de {domain}: {str(e)}")
            raise