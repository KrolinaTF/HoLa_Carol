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
from src.external_apis.pubmed_api import PubMedAPI
from src.external_apis.pubchem_api import PubChemAPI
from src.external_apis.nasa_api import NASAAPI
from src.external_apis.biological_api import UniProtAPI
from src.external_apis.trefle_api import TrefleAPI
from src.utils.translator import TranslationService

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.groq_client = GroqClient()
        self.validator = Validator()
        self.translator = TranslationService()

        # Inicializar APIs externas
        self.external_apis = {
            'pubmed': PubMedAPI(),
            'pubchem': PubChemAPI(),
            'nasa': NASAAPI(),
            'uniprot': UniProtAPI(),
            'trefle': TrefleAPI()
        }
        
        # Inicializar agentes con sus APIs correspondientes
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
        Procesa una consulta coordinando múltiples agentes y APIs externas.
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
            
            # Recopilar datos de APIs externas
            api_data = await self._gather_api_data(query)
            
            # Enriquecer el contexto con datos de APIs
            enriched_context = {
                **(context or {}),
                "api_data": api_data
            }
            
            # Obtener respuestas de cada agente
            responses = {}
            for domain, agent in self.agents.items():
                try:
                    agent_response = await agent.process_query(query, enriched_context)
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
                enriched_context
            )

            # Añadir fuentes de APIs a la respuesta
            integrated_response["api_sources"] = api_data

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

    async def _gather_api_data(self, query: str) -> Dict[str, Any]:
        """
        Recopila datos de todas las APIs externas.
        """
        api_data = {}
        try:
            # Obtener datos de PubMed
            api_data['pubmed'] = await self.external_apis['pubmed'].search_articles(query)
            
            # Obtener datos de PubChem
            api_data['pubchem'] = await self.external_apis['pubchem'].search_compound(query)
            
            # Obtener datos de NASA
            api_data['nasa'] = await self.external_apis['nasa'].get_space_weather()
            
            # Obtener datos de UniProt
            api_data['uniprot'] = await self.external_apis['uniprot'].search_proteins(query)
            
            # Obtener datos de Trefle
            api_data['trefle'] = await self.external_apis['trefle'].search_plants(query)
            
        except Exception as e:
            logger.error(f"Error recopilando datos de APIs: {str(e)}")
        
        return api_data

    async def _integrate_responses(
        self,
        responses: Dict[str, Any],
        original_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            # Crear prompt de integración
            integration_prompt = self._create_integration_prompt(
                responses,
                original_query,
                context
            )

            # Traducir el prompt si es necesario para Groq
            english_prompt = self.translator.to_english(integration_prompt)

            # Obtener respuesta integrada del LLM
            english_response = await self.groq_client.generate_response(
                english_prompt,
                temperature=0.7
            )

            # Traducir la respuesta de vuelta a español
            spanish_response = self.translator.to_spanish(english_response)

            # Calcular confianza promedio
            confidence = self._calculate_average_confidence(responses)

            return {
                "response": spanish_response,
                "confidence": confidence,
                "sources": responses
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

        # Añadir información de APIs si está disponible
        if context and "api_data" in context:
            integration_prompt += "\n\nDatos de fuentes externas:"
            for api_name, api_data in context["api_data"].items():
                integration_prompt += f"\n{api_name.upper()}: {str(api_data)}"

        integration_prompt += """
        
        Basándote en los análisis anteriores y los datos de fuentes externas, proporciona una respuesta integrada que:
        1. Sintetice la información de todos los dominios relevantes y fuentes externas
        2. Identifique y explique las interacciones entre dominios
        3. Presente una conclusión holística y recomendaciones prácticas
        4. Mantenga el rigor científico y la precisión técnica
        5. Cite las fuentes externas cuando sea relevante
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