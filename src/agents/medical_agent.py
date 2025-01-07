from typing import Dict, Any
from .base_agent import BaseAgent


class MedicalAgent(BaseAgent):
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            # Lógica específica para procesar consultas médicas
            response = {
                "response": "Análisis médico generado.",
                "confidence": 0.93
            }
            return response
        except Exception as e:
            return self.handle_error(e)

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        # Validar si la respuesta médica tiene confianza suficiente
        if response.get("confidence", 0) > 0.85:
            # Comprobar que contenga términos médicos relevantes
            keywords = ["diagnóstico", "síntoma", "tratamiento", "paciente", "patología", "prevención", "prognosis", "salud pública", "biocompatibilidad", "interacción molecular"]
            return any(keyword in response.get("response", "") for keyword in keywords)
        return False
