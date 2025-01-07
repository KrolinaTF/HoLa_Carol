from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.orchestrator.orchestrator import Orchestrator
import logging
from src.utils.database import get_session, Query, QueryResult

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

class BotanicalQuery(BaseModel):
    query: str
    user_id: str
    context: Dict[str, Any] = {}

class BotanicalResponse(BaseModel):
    response: str
    sources: list = []
    confidence: float

@router.post("/botanical/query")
async def process_botanical_query(query: BotanicalQuery):
    session = get_session()
    try:
        # Guardar la consulta
        db_query = Query(
            user_id=query.user_id,
            query_text=query.query
        )
        session.add(db_query)
        
        # Procesar la consulta con el orchestrator
        result = await orchestrator.process_query(
            query=query.query,
            user_id=query.user_id,
            context=query.context
        )
        
        # Guardar el resultado
        db_result = QueryResult(
            query=db_query,
            response=result.response,
            confidence=result.confidence,
            domain='botanical'
        )
        session.add(db_result)
        session.commit()
        
        return result
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()