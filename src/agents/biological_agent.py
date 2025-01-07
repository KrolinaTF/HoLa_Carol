from .base_agent import BaseAgent
from typing import Dict, Any

class BiologicalAgent(BaseAgent):
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Lógica específica para procesar consultas biológicas
            response = {
                "response": "Análisis biológico generado.",
                "confidence": 0.87
            }
            return response
        except Exception as e:
            return self.handle_error(e)

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        # Validar si la respuesta biológica tiene confianza suficiente
        if response.get("confidence", 0) > 0.8:
            # Comprobar que la respuesta contenga términos biológicos relevantes
            keywords = ["célula", "gen", "proteína", "metabolismo", "organismo", "homeostasis", "interacción celular", "mutación genética", "biorritmo", "metabolismo cruzado", "respuesta inmune"]
            return any(keyword in response.get("response", "") for keyword in keywords)
        return False
