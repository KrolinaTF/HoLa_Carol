from typing import Dict, Any
from .base_agent import BaseAgent
from src.external_apis.pubmed_api import PubMedAPI
import logging

logger = logging.getLogger(__name__)


class MedicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.pubmed_api = PubMedAPI()

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Obtener información de PubMed
            scientific_articles = await self.pubmed_api.search_articles(query)
            
            # Incorporar la información en el contexto
            enriched_context = {
                **(context or {}),
                "scientific_articles": scientific_articles
            }
            
            # Procesar con el LLM
            response = {
                "response": "Análisis médico generado con información de PubMed.",
                "confidence": 0.93,
                "sources": scientific_articles
            }
            
            return response
        except Exception as e:
            return self.handle_error(e)

    async def validate_response(self, response_data: Dict[str, Any]) -> bool:
        # Usamos el parámetro response_data en lugar de response
        if response_data.get("confidence", 0) > 0.85:
            keywords = ["diagnóstico", "síntoma", "tratamiento", "paciente", 
                       "patología", "prevención", "prognosis"]
            return any(keyword in response_data.get("response", "") for keyword in keywords)
        return False
