import requests
from typing import List, Dict
import os
import logging
from src.utils.translator import TranslationService

logger = logging.getLogger(__name__)

class TrefleAPI:
    def __init__(self):
        self.api_key = os.getenv("TREFLE_API_KEY")
        self.base_url = "https://trefle.io/api/v1"
        self.translator = TranslationService()
        
    async def search_plants(self, query: str) -> List[Dict]:
        try:
            # Traducir la consulta al inglés
            english_query = self.translator.to_english(query)
            logger.info(f"Consulta traducida: {english_query}")

            response = requests.get(
                f"{self.base_url}/plants/search",
                params={
                    "token": self.api_key,
                    "q": english_query
                }
            )
            
            if response.ok:
                data = response.json()
                # Traducir los resultados relevantes
                translated_results = []
                
                for plant in data.get('data', []):
                    translated_plant = {
                        "nombre_comun": self.translator.to_spanish(plant.get('common_name', '')),
                        "nombre_cientifico": plant.get('scientific_name', ''),
                        "familia": self.translator.to_spanish(plant.get('family', '')),
                        "usos": self.translator.to_spanish(plant.get('uses', [])),
                        "id": plant.get('id', '')
                    }
                    translated_results.append(translated_plant)
                
                return translated_results
            
            return []

        except Exception as e:
            logger.error(f"Error accessing Trefle: {str(e)}")
            return []