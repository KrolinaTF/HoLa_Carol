from typing import Dict, List

class BiologicalPrompts:
    # Prompt base para consultas médicas generales
    BASE_PROMPT = """Analiza la siguiente consulta biológica teniendo en cuenta el conocimiento médico, 
    botánico y otros factores relevantes para la salud. Proporciona una respuesta basada en evidencia:
    
    CONSULTA: {query}
    CONTEXTO ADICIONAL: {context}
    """

    # Prompt para validación de interacciones
    INTERACTION_VALIDATION = """Verifica las posibles interacciones entre los siguientes elementos:
    ELEMENTOS: {elements}
    TIPO DE INTERACCIÓN: {interaction_type}
    """

    # Prompt para recomendaciones holísticas
    HOLISTIC_RECOMMENDATIONS = """Proporciona recomendaciones holísticas considerando:
    CONDICIÓN: {condition}
    FACTORES AMBIENTALES: {environmental_factors}
    ESTILO DE VIDA: {lifestyle_factors}
    """

    @staticmethod
    def get_base_prompt(query: str, context: Dict = None) -> str:
        """
        Genera el prompt base con la consulta y contexto.
        """
        context_str = str(context) if context else "No hay contexto adicional"
        return BiologicalPrompts.BASE_PROMPT.format(
            query=query,
            context=context_str
        )

    @staticmethod
    def get_interaction_prompt(elements: List[str], interaction_type: str) -> str:
        """
        Genera el prompt para validar interacciones.
        """
        elements_str = ", ".join(elements)
        return BiologicalPrompts.INTERACTION_VALIDATION.format(
            elements=elements_str,
            interaction_type=interaction_type
        )

    @staticmethod
    def get_holistic_prompt(
        condition: str,
        environmental_factors: List[str],
        lifestyle_factors: List[str]
    ) -> str:
        """
        Genera el prompt para recomendaciones holísticas.
        """
        return BiologicalPrompts.HOLISTIC_RECOMMENDATIONS.format(
            condition=condition,
            environmental_factors=", ".join(environmental_factors),
            lifestyle_factors=", ".join(lifestyle_factors)
        )
