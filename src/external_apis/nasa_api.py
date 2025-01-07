import requests
from typing import Dict, Optional
import logging
import os
from datetime import datetime
from src.utils.translator import TranslationService

logger = logging.getLogger(__name__)

class NASAAPI:
    def __init__(self):
        self.api_key = os.getenv("NASA_API_KEY")
        self.base_url = "https://api.nasa.gov"
        self.translator = TranslationService()

    async def get_relevant_data(self, query: str) -> Dict:
        """Obtiene datos relevantes basados en la consulta"""
        try:
            # Traducir la consulta al inglés
            english_query = self.translator.to_english(query)
            logger.info(f"Consulta traducida: {english_query}")

            data = {}
            
            # APOD para información general
            apod_data = await self.get_astronomy_picture()
            if apod_data:
                data['apod'] = {
                    'titulo': self.translator.to_spanish(apod_data.get('title', '')),
                    'explicacion': self.translator.to_spanish(apod_data.get('explanation', '')),
                    'fecha': apod_data.get('date', '')
                }

            # Datos de la Tierra si son relevantes
            if any(term in english_query.lower() for term in ['earth', 'radiation', 'magnetic field', 'atmosphere']):
                earth_data = await self.get_earth_data()
                if earth_data:
                    data['earth'] = {
                        'datos': self.translator.to_spanish(earth_data)
                    }

            return data if data else {"mensaje": "No se encontraron datos relevantes"}

        except Exception as e:
            logger.error(f"Error accessing NASA API: {str(e)}")
            return {"error": str(e)}

    async def get_astronomy_picture(self) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/planetary/apod",
                params={"api_key": self.api_key}
            )
            return response.json() if response.ok else None
        except Exception as e:
            logger.error(f"Error getting APOD: {str(e)}")
            return None

    async def get_earth_data(self) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/EPIC/api/natural",
                params={"api_key": self.api_key}
            )
            return response.json() if response.ok else None
        except Exception as e:
            logger.error(f"Error getting Earth data: {str(e)}")
            return None