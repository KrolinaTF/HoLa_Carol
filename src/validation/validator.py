from typing import Dict, Any
from src.utils.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class Validator:
    def __init__(self):
        self.confidence_thresholds = {
            'medical': 0.85,
            'botanical': 0.80,
            'chemical': 0.80,
            'physical': 0.80,
            'biological': 0.80
        }

    def validate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida las respuestas de todos los agentes según su dominio.
        """
        validated_responses = {}
        
        for domain, response in responses.items():
            try:
                if self._validate_response_structure(response):
                    if self._validate_domain_specific(domain, response):
                        validated_responses[domain] = response
                    else:
                        logger.warning(f"Respuesta de {domain} no cumple validación específica")
            except ValidationError as e:
                logger.error(f"Error validando respuesta de {domain}: {str(e)}")

        return validated_responses

    def _validate_response_structure(self, response: Dict[str, Any]) -> bool:
        """
        Valida la estructura básica de una respuesta.
        """
        try:
            if not isinstance(response, dict):
                raise ValidationError("La respuesta debe ser un diccionario")
            
            required_fields = ['response', 'confidence']
            for field in required_fields:
                if field not in response:
                    raise ValidationError(f"Campo requerido ausente: {field}")
                    
            return True
        except Exception as e:
            logger.error(f"Error en validación de estructura: {str(e)}")
            return False

    def _validate_domain_specific(self, domain: str, response: Dict[str, Any]) -> bool:
        """
        Aplica validaciones específicas según el dominio.
        """
        try:
            # Verificar umbral de confianza específico del dominio
            threshold = self.confidence_thresholds.get(domain, 0.8)
            if response.get('confidence', 0) < threshold:
                return False

            return True
        except Exception as e:
            logger.error(f"Error en validación específica de dominio: {str(e)}")
            return False