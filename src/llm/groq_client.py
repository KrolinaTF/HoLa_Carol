from typing import Optional, Dict
import os
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no encontrada en variables de entorno")
        
        self.base_url = "https://api.groq.com/v1"
        self.model = "llama2-70b-4096"  # Puedes cambiar el modelo según necesites
        
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict] = None
    ) -> str:
        """
        Genera una respuesta usando la API de Groq.
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if context:
                # Añade contexto al prompt si existe
                data["messages"].insert(0, {
                    "role": "system",
                    "content": str(context)
                })

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("No se recibió respuesta válida de Groq")

        except httpx.TimeoutException:
            logger.error("Timeout al conectar con Groq API")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al conectar con Groq API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al generar respuesta: {str(e)}")
            raise

    async def get_embedding(self, text: str) -> list:
        """
        Obtiene embeddings para el texto dado.
        Como Groq actualmente no proporciona API de embeddings,
        usaremos una alternativa como el modelo all-MiniLM-L6-v2
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            # Inicializar el modelo (esto debería moverse al __init__ en producción)
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Generar embedding
            embedding = model.encode(text)
            
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            raise