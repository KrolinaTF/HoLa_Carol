import pytest
from sqlalchemy.orm import Session
from src.utils.database import init_db, get_session, User, Query, QueryResult

@pytest.fixture
def test_db():
    # Usar una base de datos en memoria para tests
    engine = init_db("sqlite:///:memory:")
    return engine

@pytest.fixture
def session(test_db):
    Session = get_session()
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_create_user(session):
    user = User(username="test_user")
    session.add(user)
    session.commit()
    
    assert user.id is not None
    assert user.username == "test_user"

def test_create_query(session):
    user = User(username="test_user")
    session.add(user)
    session.commit()
    
    query = Query(
        user_id=user.id,
        query_text="test query"
    )
    session.add(query)
    session.commit()
    
    assert query.id is not None
    assert query.user_id == user.id

def test_create_query_result(session):
    user = User(username="test_user")
    session.add(user)
    session.commit()
    
    query = Query(user_id=user.id, query_text="test query")
    session.add(query)
    session.commit()
    
    result = QueryResult(
        query_id=query.id,
        response="test response",
        confidence=0.9,
        domain="test"
    )
    session.add(result)
    session.commit()
    
    assert result.id is not None
    assert result.confidence == 0.9