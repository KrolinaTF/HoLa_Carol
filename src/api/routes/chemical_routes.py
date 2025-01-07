from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.orchestrator.orchestrator import Orchestrator
import logging
from src.utils.database import get_session, Query, QueryResult

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

orchestrator = Orchestrator()


class ChemicalQuery(BaseModel):
    query: str
    user_id: str
    context: Dict[str, Any] = {}

class ChemicalResponse(BaseModel):
    response: str
    sources: list = []
    confidence: float

@router.post("/chemical/query", response_model=ChemicalResponse)
async def process_chemical_query(query: ChemicalQuery):
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
            domain='chemical'
        )
        session.add(db_result)
        session.commit()
        
        return ChemicalResponse(
            response=result['response'],
            confidence=result['confidence'],
            sources=result.get('sources', {}),
            api_sources=result.get('api_sources', {})
        )

    except Exception as e:
        session.rollback()
        logger.error(f"Error processing chemical query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()