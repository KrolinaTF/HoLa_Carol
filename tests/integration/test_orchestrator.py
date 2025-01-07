import pytest
from src.orchestrator.orchestrator import Orchestrator
from src.utils.exceptions import ExpertSystemException

@pytest.fixture
def orchestrator():
    return Orchestrator()

async def test_orchestrator_initialization(orchestrator):
    assert orchestrator.agents is not None
    assert len(orchestrator.agents) == 5  # medical, botanical, chemical, physical, biological
    assert orchestrator.groq_client is not None
    assert orchestrator.validator is not None

async def test_process_query(orchestrator):
    query = "¿Cómo afecta la radiación de microondas a las plantas medicinales?"
    user_id = "test_user"
    result = await orchestrator.process_query(query, user_id)
    
    assert isinstance(result, dict)
    assert "response" in result
    assert "confidence" in result
    assert "sources" in result
    assert result["confidence"] > 0.7

async def test_integrate_responses(orchestrator):
    responses = {
        "medical": {"response": "Respuesta médica", "confidence": 0.9},
        "botanical": {"response": "Respuesta botánica", "confidence": 0.85},
        "physical": {"response": "Respuesta física", "confidence": 0.88}
    }
    query = "consulta de prueba"
    
    result = await orchestrator._integrate_responses(responses, query)
    assert "response" in result
    assert "confidence" in result
    assert result["confidence"] > 0.8

async def test_error_handling(orchestrator):
    with pytest.raises(ExpertSystemException):
        await orchestrator.process_query("", "test_user")  # Query vacía debería fallar

@pytest.mark.parametrize("query,expected_domains", [
    ("efectos de la radiación", ["physical", "medical"]),
    ("plantas medicinales", ["botanical", "medical"]),
    ("reacciones químicas en células", ["chemical", "biological"])
])
async def test_domain_specific_queries(orchestrator, query, expected_domains):
    result = await orchestrator.process_query(query, "test_user")
    assert result is not None
    assert any(domain in str(result["sources"]) for domain in expected_domains)