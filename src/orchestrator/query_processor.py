from typing import Dict, Any, List, Optional
import logging
import re
from src.rag.retriever.document_retriever import DocumentRetriever
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        self.document_retriever = DocumentRetriever()

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una consulta y prepara la información necesaria para los agentes.
        """
        try:
            # Limpiar y normalizar la consulta
            processed_query = self._clean_query(query)
            
            # Identificar dominios relevantes
            domains = self._identify_domains(processed_query)
            
            # Recuperar información relevante de la base de conocimiento
            relevant_docs = await self._retrieve_relevant_documents(processed_query, domains)
            
            # Estructurar la información para los agentes
            structured_data = self._structure_data(
                processed_query,
                relevant_docs,
                domains,
                context
            )

            return structured_data

        except Exception as e:
            logger.error(f"Error procesando consulta: {str(e)}")
            raise

    def _clean_query(self, query: str) -> str:
        """
        Limpia y normaliza la consulta.
        """
        # Convertir a minúsculas
        query = query.lower()
        
        # Eliminar caracteres especiales
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # Eliminar espacios múltiples
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query

    def _identify_domains(self, query: str) -> List[str]:
        """
        Identifica qué dominios son relevantes para la consulta.
        """
        domains = []
        
        # Palabras clave por dominio
        domain_keywords = {
            'medical': ['enfermedad', 'síntoma', 'diagnóstico', 'tratamiento', 'salud'],
            'botanical': ['planta', 'hierba', 'natural', 'botánico', 'vegetal'],
            'chemical': ['químico', 'compuesto', 'reacción', 'sustancia'],
            'physical': ['física', 'radiación', 'energía', 'frecuencia', 'ondas'],
            'biological': ['biológico', 'celular', 'organismo', 'tejido']
        }

        # Comprobar palabras clave en la consulta
        for domain, keywords in domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                domains.append(domain)

        # Si no se identifica ningún dominio, incluir todos
        if not domains:
            domains = list(domain_keywords.keys())

        return domains

    async def _retrieve_relevant_documents(
        self,
        query: str,
        domains: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recupera documentos relevantes para la consulta de cada dominio.
        """
        relevant_docs = {}
        
        for domain in domains:
            try:
                docs = await self.document_retriever.get_relevant_documents(
                    query=query,
                    domain=domain,
                    num_documents=3  # Ajustar según necesidades
                )
                relevant_docs[domain] = docs
            except Exception as e:
                logger.error(f"Error recuperando documentos para {domain}: {str(e)}")
                relevant_docs[domain] = []

        return relevant_docs

    def _structure_data(
        self,
        query: str,
        relevant_docs: Dict[str, List[Dict[str, Any]]],
        domains: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estructura la información para su uso por los agentes.
        """
        structured_data = {
            "original_query": query,
            "processed_query": self._clean_query(query),
            "domains": domains,
            "relevant_documents": relevant_docs,
            "context": context or {},
            "metadata": {
                "timestamp": self._get_current_timestamp(),
                "num_domains": len(domains),
                "num_documents": sum(len(docs) for docs in relevant_docs.values())
            }
        }

        return structured_data

    @staticmethod
    def _get_current_timestamp() -> str:
        """
        Obtiene el timestamp actual en formato ISO.
        """
        return datetime.datetime.now().isoformat()