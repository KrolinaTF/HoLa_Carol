import requests
from typing import List, Dict
import logging
from src.utils.translator import TranslationService

logger = logging.getLogger(__name__)

class PubMedAPI:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.translator = TranslationService()
        
    async def search_articles(self, query: str, max_results: int = 5) -> List[Dict]:
        try:
            # Traducir la consulta al inglés
            english_query = self.translator.to_english(query)
            logger.info(f"Consulta traducida: {english_query}")

            # Búsqueda en PubMed
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": english_query,
                "retmax": max_results,
                "retmode": "json"
            }
            response = requests.get(search_url, params=params)
            ids = response.json()["esearchresult"]["idlist"]
            
            # Obtener detalles de los artículos
            details_url = f"{self.base_url}esummary.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json"
            }
            details = requests.get(details_url, params=params)
            
            # Traducir los resultados al español
            results = [details.json()["result"][id] for id in ids]
            translated_results = []
            
            for result in results:
                translated_result = {
                    "title": self.translator.to_spanish(result.get("title", "")),
                    "abstract": self.translator.to_spanish(result.get("abstract", "")),
                    "id": result.get("uid", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{result.get('uid', '')}"
                }
                translated_results.append(translated_result)
            
            return translated_results

        except Exception as e:
            logger.error(f"Error accessing PubMed: {str(e)}")
            return []