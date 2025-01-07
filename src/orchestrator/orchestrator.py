from typing import Dict, Any, Optional
import logging
from src.agents.medical_agent import MedicalAgent
from src.agents.botanical_agent import BotanicalAgent
from src.agents.chemical_agent import ChemicalAgent
from src.agents.physical_agent import PhysicalAgent
from src.agents.biological_agent import BiologicalAgent
from src.validation.validator import Validator
from src.llm.groq_client import GroqClient
from src.utils.database import get_session, Query, QueryResult
from src.llm.prompt_templates.medical_prompts import MedicalPrompts
from src.llm.prompt_templates.botanical_prompts import BotanicalPrompts
from src.llm.prompt_templates.chemical_prompts import ChemicalPrompts
from src.llm.prompt_templates.physical_prompts import PhysicalPrompts
from src.llm.prompt_templates.biological_prompts import BiologicalPrompts

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.groq_client = GroqClient()
        self.validator = Validator()
        
        # Inicializar agentes
        self.agents = {
            'medical': MedicalAgent(),
            'botanical': BotanicalAgent(),
            'chemical': ChemicalAgent(),
            'physical': PhysicalAgent(),
            'biological': BiologicalAgent()
        }
        
        # Inicializar prompts
        self.prompts = {
            'medical': MedicalPrompts(),
            'botanical': BotanicalPrompts(),
            'chemical': ChemicalPrompts(),
            'physical': PhysicalPrompts(),
            'biological': BiologicalPrompts()
        }

    async def process_query(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una consulta coordinando múltiples agentes.
        """
        logger.info(f"Procesando consulta: {query}")
        try:
            # Iniciar sesión de base de datos
            session = get_session()
            
            # Guardar consulta inicial
            db_query = Query(
                user_id=user_id,
                query_text=query
            )
            session.add(db_query)
            
            # Obtener respuestas de cada agente
            responses = {}
            for domain, agent in self.agents.items():
                try:
                    agent_response = await agent.process_query(query, context)
                    responses[domain] = agent_response
                except Exception as e:
                    logger.error(f"Error en agente {domain}: {str(e)}")
                    responses[domain] = {"error": str(e)}

            # Validar respuestas
            validated_responses = self.validator.validate_responses(responses)

            # Integrar respuestas
            integrated_response = await self._integrate_responses(
                validated_responses,
                query,
                context
            )

            # Guardar resultado
            result = QueryResult(
                query=db_query,
                response=integrated_response['response'],
                confidence=integrated_response['confidence'],
                domain='integrated'
            )
            session.add(result)
            session.commit()

            return integrated_response

        except Exception as e:
            logger.error(f"Error en orchestrator: {str(e)}")
            if 'session' in locals():
                session.rollback()
            raise
        finally:
            if 'session' in locals():
                session.close()

    async def _integrate_responses(
        self,
        responses: Dict[str, Any],
        original_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Integra las respuestas de diferentes agentes en una respuesta coherente.
        """
        try:
            # Crear prompt de integración
            integration_prompt = self._create_integration_prompt(
                responses,
                original_query,
                context
            )

            # Obtener respuesta integrada del LLM
            integrated_text = await self.groq_client.generate_response(
                integration_prompt,
                temperature=0.7
            )

            # Calcular confianza promedio
            confidence = self._calculate_average_confidence(responses)

            return {
                "response": integrated_text,
                "confidence": confidence,
                "sources": responses  # Incluir respuestas originales
            }

        except Exception as e:
            logger.error(f"Error en integración de respuestas: {str(e)}")
            raise

    def _create_integration_prompt(
        self,
        responses: Dict[str, Any],
        original_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crea un prompt para integrar las respuestas usando los prompts específicos de cada dominio.
        """
        integration_prompt = f"""
        Consulta original: {original_query}

        Análisis por dominio:
        """

        for domain, response in responses.items():
            if isinstance(response, dict) and 'response' in response:
                domain_prompt = self.prompts[domain].get_base_prompt(
                    response['response'],
                    context
                )
                integration_prompt += f"\n{domain.upper()}: {domain_prompt}"

        integration_prompt += """
        
        Basándote en los análisis anteriores, proporciona una respuesta integrada que:
        1. Sintetice la información de todos los dominios relevantes
        2. Identifique y explique las interacciones entre dominios
        3. Presente una conclusión holística y recomendaciones prácticas
        4. Mantenga el rigor científico y la precisión técnica
        """

        return integration_prompt

    def _calculate_average_confidence(self, responses: Dict[str, Any]) -> float:
        """
        Calcula la confianza promedio de todas las respuestas.
        """
        confidences = []
        for response in responses.values():
            if isinstance(response, dict) and 'confidence' in response:
                confidences.append(response['confidence'])
        
        return sum(confidences) / len(confidences) if confidences else 0.0