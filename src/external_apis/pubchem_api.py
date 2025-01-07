import requests
from typing import Dict
import logging
from src.utils.translator import TranslationService

logger = logging.getLogger(__name__)

class PubChemAPI:
    def __init__(self):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.translator = TranslationService()
        
    async def search_compound(self, query: str) -> Dict:
        try:
            # Traducir la consulta al inglés
            english_query = self.translator.to_english(query)
            logger.info(f"Consulta traducida: {english_query}")

            # Búsqueda por nombre
            response = requests.get(
                f"{self.base_url}/compound/name/{english_query}/JSON"
            )
            
            if response.ok:
                data = response.json()
                # Traducir la información relevante al español
                translated_data = {
                    "nombre": self.translator.to_spanish(data.get("PC_Compounds", [])[0].get("PC_Compounds_id_name", "")),
                    "descripcion": self.translator.to_spanish(data.get("PC_Compounds", [])[0].get("PC_Compounds_props", {}).get("description", "")),
                    "id": data.get("PC_Compounds", [])[0].get("id", {}).get("id", {}).get("cid", "")
                }
                return translated_data
            return {"error": "No se encontraron datos", "details": response.text}

        except Exception as e:
            logger.error(f"Error accessing PubChem: {str(e)}")
            return {"error": str(e)}