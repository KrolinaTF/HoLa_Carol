from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.utils.exceptions import AgentError
from src.utils.logger import setup_logger

logger = setup_logger()

class BaseAgent(ABC):
    def __init__(self):
        self.logger = logger

    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def validate_response(self, response: Dict[str, Any]) -> bool:
        pass
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Maneja y registra errores"""
        self.logger.error(f"Error en {self.__class__.__name__}: {str(error)}")
        return {
            "status": "error",
            "message": str(error),
            "agent": self.__class__.__name__
        }