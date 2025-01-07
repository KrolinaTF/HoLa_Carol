from typing import Dict, Any
from .base_agent import BaseAgent


class ChemicalAgent(BaseAgent):
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Lógica específica para procesar consultas químicas
            response = {
                "response": "Análisis químico generado.",
                "confidence": 0.88
            }
            return response
        except Exception as e:
            return self.handle_error(e)

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        # Validar si la respuesta química tiene confianza suficiente
        if response.get("confidence", 0) > 0.8:
            # Comprobar que la respuesta contenga términos químicos conocidos
            keywords = ["mol", "reacción", "ácido", "base", "catalizador", "vitamina", "compuesto", "solubilidad", "electrón", "hidrólisis", "metabolito", "reacción enzimática", "biosíntesis"]
            return any(keyword in response.get("response", "") for keyword in keywords)
        return False
