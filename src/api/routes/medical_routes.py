from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from src.orchestrator.orchestrator import Orchestrator
import logging
from src.utils.database import get_session, Query, QueryResult

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

orchestrator = Orchestrator()

class MedicalQuery(BaseModel):
    query: str
    user_id: str
    context: Dict[str, Any] = {}


class MedicalResponse(BaseModel):
    response: str
    sources: list = []
    confidence: float

@router.post("/medical/query")
async def process_medical_query(query: MedicalQuery):
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
            response=result['response'],
            confidence=result['confidence'],
            domain='medical'
        )
        session.add(db_result)
        session.commit()
        
        return result
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
