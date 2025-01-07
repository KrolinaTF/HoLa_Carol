from typing import Dict, Any
from .base_agent import BaseAgent
from src.external_apis.pubchem_api import PubChemAPI
import logging

logger = logging.getLogger(__name__)


class ChemicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.pubchem_api = PubChemAPI()

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Obtener información química de PubChem
            chemical_data = await self.pubchem_api.search_compound(query)
            
            # Construir la respuesta directamente
            response = {
                "response": "Análisis químico generado con información de PubChem.",
                "confidence": 0.92,
                "sources": chemical_data
            }
            
            return response
        except Exception as e:
            return self.handle_error(e)
        
    async def validate_response(self, response_data: Dict[str, Any]) -> bool:
        if response_data.get("confidence", 0) > 0.80:
            keywords = ["mol", "reacción", "ácido", "base", "catalizador", 
                    "vitamina", "compuesto", "solubilidad", "electrón", 
                    "hidrólisis", "metabolito", "reacción enzimática", "biosíntesis"]
            return any(keyword in response_data.get("response", "") for keyword in keywords)
        return False