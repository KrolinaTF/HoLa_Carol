from typing import Dict, Any
from .base_agent import BaseAgent
import logging
from src.external_apis.trefle_api import TrefleAPI

logger = logging.getLogger(__name__)

class BotanicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.trefle_api = TrefleAPI()

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Obtener datos botánicos de Trefle
            plant_data = await self.trefle_api.search_plants(query)
            
            # Asegurar una respuesta válida
            response = {
                "response": "Análisis botánico generado",
                "confidence": 0.85,
                "sources": []
            }

            if plant_data:
                response["sources"] = plant_data
                response["confidence"] = 0.90
                # Construir una respuesta más detallada si hay datos
                if isinstance(plant_data, dict) and plant_data.get('data'):
                    num_plants = len(plant_data['data'])
                    response["response"] = f"Análisis botánico basado en {num_plants} especies de plantas encontradas"

            return response
        except Exception as e:
            logger.error(f"Error en BotanicalAgent: {str(e)}")
            return self.handle_error(e)
        
    async def validate_response(self, response_data: Dict[str, Any]) -> bool:
        if response_data.get("confidence", 0) > 0.80:
            # Comprobar que la respuesta contenga términos botánicos relevantes
            keywords = ["planta", "raíz", "hoja", "fotosíntesis", "fitoterapia", 
                    "especie", "hierba", "extracto", "nutriente", "antioxidante", 
                    "alcaloide", "flavonoide"]
            return any(keyword in response_data.get("response", "") for keyword in keywords)
        return False
