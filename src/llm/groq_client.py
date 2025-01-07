from groq import Groq
import os
import logging
from typing import Optional, Dict
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no encontrada en variables de entorno")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # El modelo específico que nos proporcionan
        
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict] = None
    ) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            if context:
                messages.insert(0, {
                    "role": "system",
                    "content": str(context)
                })

            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generando respuesta con Groq: {str(e)}")
            raise

    async def get_embedding(self, text: str) -> list:
        """
        Obtiene embeddings para el texto dado.
        Como Groq actualmente no proporciona API de embeddings,
        usaremos una alternativa como el modelo all-MiniLM-L6-v2
        """
        try:
            # Inicializar el modelo (esto debería moverse al __init__ en producción)
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Generar embedding
            embedding = model.encode(text)
            
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            raise