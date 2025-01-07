from typing import List, Union
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa el gestor de embeddings usando un modelo de sentence-transformers.
        """
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            logger.info(f"EmbeddingManager inicializado con modelo {model_name}")
        except Exception as e:
            logger.error(f"Error inicializando EmbeddingManager: {str(e)}")
            raise

    @lru_cache(maxsize=1000)
    def get_embedding(self, text: str) -> List[float]:
        """
        Genera embeddings para un texto dado.
        """
        try:
            # Preprocesar y tokenizar el texto
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            # Generar embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = self._mean_pooling(outputs, inputs['attention_mask'])
                
            # Convertir a lista y normalizar
            return self._normalize(embeddings[0]).tolist()

        except Exception as e:
            logger.error(f"Error generando embedding: {str(e)}")
            raise

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos.
        """
        try:
            # Procesar en lotes para eficiencia
            embeddings = []
            batch_size = 32
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = [self.get_embedding(text) for text in batch_texts]
                embeddings.extend(batch_embeddings)
            
            return embeddings

        except Exception as e:
            logger.error(f"Error generando embeddings en lote: {str(e)}")
            raise

    def _mean_pooling(self, model_output, attention_mask) -> torch.Tensor:
        """
        Realiza mean pooling sobre los tokens del último hidden state.
        """
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def _normalize(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Normaliza los embeddings.
        """
        return embeddings / embeddings.norm(dim=-1, keepdim=True)

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula la similitud coseno entre dos embeddings.
        """
        try:
            e1 = np.array(embedding1)
            e2 = np.array(embedding2)
            return float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))
        except Exception as e:
            logger.error(f"Error calculando similitud: {str(e)}")
            raise