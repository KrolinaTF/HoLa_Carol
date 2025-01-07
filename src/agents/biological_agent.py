from .base_agent import BaseAgent
from typing import Dict, Any
from src.external_apis.biological_api import UniProtAPI
import logging

logger = logging.getLogger(__name__)


class BiologicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.uniprot_api = UniProtAPI()

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Obtener información biológica de UniProt
            protein_data = await self.uniprot_api.search_proteins(query)
            
            # Construir la respuesta directamente
            response = {
                "response": "Análisis biológico generado con información de UniProt.",
                "confidence": 0.91,
                "sources": protein_data
            }
            
            return response
        except Exception as e:
            return self.handle_error(e)
    
    async def validate_response(self, response_data: Dict[str, Any]) -> bool:
        if response_data.get("confidence", 0) > 0.80:
            keywords = ["célula", "gen", "proteína", "metabolismo", "organismo", 
                    "homeostasis", "interacción celular", "mutación genética", 
                    "biorritmo", "metabolismo cruzado", "respuesta inmune"]
            return any(keyword in response_data.get("response", "") for keyword in keywords)
        return False
