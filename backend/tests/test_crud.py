import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models, crud
from database import Base


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_travel_record_and_points(memory_db):
    # create a user
    user = crud.create_user(memory_db, type('U', (), {'username': 'tester', 'password': 'pass'}))
    # create travel record
    tr = crud.create_travel_record(memory_db, user.id, 'bicycle', 5.0, 5.0, 15)
    assert tr.transport_mode == 'bicycle'
    # user's points updated
    u = crud.get_user(memory_db, user.id)
    assert u.eco_points >= 15


def test_compute_sustainability_score(memory_db):
    user = crud.create_user(memory_db, type('U', (), {'username': 'scoreuser', 'password': 'pw'}))
    # add a carbon calculation
    crud.add_carbon_calculation(memory_db, user_id=user.id, source='test', amount_kg=10.0, confidence=0.9)
    ss = crud.compute_sustainability_score(memory_db, user.id)
    assert ss is not None
    assert 0 <= ss.green_impact_score <= 100
    assert ss.sustainability_grade in ['A','B','C','D','F']
