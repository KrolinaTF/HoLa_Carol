from typing import Dict, Any
from .base_agent import BaseAgent

class BotanicalAgent(BaseAgent):
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Lógica específica para procesar consultas botánicas
            response = {
                "response": "Análisis botánico generado.",
                "confidence": 0.90
            }
            return response
        except Exception as e:
            return self.handle_error(e)

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        # Validar si la respuesta botánica tiene confianza suficiente
        if response.get("confidence", 0) > 0.8:
            # Comprobar que la respuesta contenga palabras clave botánicas
            keywords = ["planta", "raíz", "hoja", "fotosíntesis", "fitoterapia", "especie", "hierba", "extracto", "nutriente", "antioxidante", "alcaloide", "flavonoide"]
            return any(keyword in response.get("response", "") for keyword in keywords)
        return False
