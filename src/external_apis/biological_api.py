import requests
from typing import Dict
import logging
from src.utils.translator import TranslationService

logger = logging.getLogger(__name__)

class UniProtAPI:
    def __init__(self):
        self.base_url = "https://rest.uniprot.org/uniprotkb/search"
        self.translator = TranslationService()
        
    async def search_proteins(self, query: str) -> Dict:
        try:
            # Traducir la consulta al inglés
            english_query = self.translator.to_english(query)
            logger.info(f"Consulta traducida: {english_query}")

            response = requests.get(
                self.base_url,
                params={
                    "query": english_query,
                    "format": "json"
                }
            )
            
            if response.ok:
                data = response.json()
                # Traducir los resultados relevantes
                translated_results = []
                
                for result in data.get('results', []):
                    translated_result = {
                        "nombre": self.translator.to_spanish(result.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', '')),
                        "funcion": self.translator.to_spanish(result.get('comments', [{}])[0].get('text', [{}])[0].get('value', '')),
                        "organismo": self.translator.to_spanish(result.get('organism', {}).get('scientificName', '')),
                        "id": result.get('primaryAccession', '')
                    }
                    translated_results.append(translated_result)
                
                return translated_results
            
            return []

        except Exception as e:
            logger.error(f"Error accessing UniProt: {str(e)}")
            return []