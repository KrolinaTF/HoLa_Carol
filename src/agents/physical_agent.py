from typing import Dict, Any
from .base_agent import BaseAgent
import logging
from src.external_apis.nasa_api import NASAAPI

logger = logging.getLogger(__name__)


class PhysicalAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.nasa_api = NASAAPI()

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Obtener datos relevantes de la NASA
            nasa_data = await self.nasa_api.get_relevant_data(query)
            
            # Asegurar una respuesta válida
            response = {
                "response": "Análisis físico basado en datos de la NASA",
                "confidence": 0.85,
                "sources": nasa_data
            }

            if nasa_data:
                response["response"] = nasa_data.get('explanation', response["response"])
                response["confidence"] = 0.92

            return response
        except Exception as e:
            logger.error(f"Error en PhysicalAgent: {str(e)}")
            return self.handle_error(e)
        
    async def validate_response(self, response_data: Dict[str, Any]) -> bool:
        if response_data.get("confidence", 0) > 0.80:
            keywords = ["metro", "segundo", "newton", "joule", "radiación", 
                    "frecuencia", "campo magnético", "absorción", "densidad", 
                    "tensión superficial", "energía térmica", "conductividad"]
            return any(keyword in response_data.get("response", "") for keyword in keywords)
        return False