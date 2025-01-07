import pytest
from src.agents.medical_agent import MedicalAgent
from src.agents.botanical_agent import BotanicalAgent
from src.agents.chemical_agent import ChemicalAgent
from src.agents.physical_agent import PhysicalAgent
from src.agents.biological_agent import BiologicalAgent

@pytest.fixture
def medical_agent():
    return MedicalAgent()

@pytest.fixture
def botanical_agent():
    return BotanicalAgent()

@pytest.fixture
def chemical_agent():
    return ChemicalAgent()

@pytest.fixture
def physical_agent():
    return PhysicalAgent()

@pytest.fixture
def biological_agent():
    return BiologicalAgent()

# Tests para MedicalAgent
async def test_medical_agent_process_query(medical_agent):
    query = "¿Qué tratamiento es recomendado para la hipertensión?"
    result = await medical_agent.process_query(query)
    assert isinstance(result, dict)
    assert "response" in result
    assert "confidence" in result
    assert result["confidence"] >= 0.85

async def test_medical_agent_validate_response(medical_agent):
    response = {
        "response": "El tratamiento para la hipertensión incluye diagnóstico y medicación específica",
        "confidence": 0.9
    }
    is_valid = await medical_agent.validate_response(response)
    assert is_valid is True

# Tests similares para los otros agentes
async def test_botanical_agent_process_query(botanical_agent):
    query = "¿Qué plantas ayudan a reducir la ansiedad?"
    result = await botanical_agent.process_query(query)
    assert isinstance(result, dict)
    assert "response" in result
    assert "confidence" in result
    assert result["confidence"] >= 0.8