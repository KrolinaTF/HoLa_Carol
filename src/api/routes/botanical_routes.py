from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.orchestrator.orchestrator import Orchestrator
import logging
from src.utils.database import get_session, Query, QueryResult

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

orchestrator = Orchestrator()


class BotanicalQuery(BaseModel):
    query: str
    user_id: str
    context: Dict[str, Any] = {}

class BotanicalResponse(BaseModel):
    response: str
    sources: list = []
    confidence: float

@router.post("/botanical/query", response_model=BotanicalResponse)
async def process_botanical_query(query: BotanicalQuery):
    session = get_session()
    try:
        # Guardar la consulta
        db_query = Query(
            user_id=query.user_id,
            query_text=query.query
        )
        session.add(db_query)
        
        # Procesar con orchestrator
        result = await orchestrator.process_query(
            query=query.query,
            user_id=query.user_id,
            context=query.context
        )
        
        # Guardar resultado
        db_result = QueryResult(
            query=db_query,
            response=result['response'],
            confidence=result['confidence'],
            domain='botanical'
        )
        session.add(db_result)
        session.commit()
        
        return BotanicalResponse(
            response=result['response'],
            confidence=result['confidence'],
            sources=result.get('sources', {}),
            api_sources=result.get('api_sources', {})
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Error processing botanical query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()