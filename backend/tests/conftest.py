import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
import main
import auth
from database import Base


@pytest.fixture(scope='function')
def test_app(tmp_path):
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # patch main SessionLocal and get_db
    main.SessionLocal = TestingSessionLocal

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[main.get_db] = override_get_db
    main.app.dependency_overrides[auth.get_db] = override_get_db

    # set upload dir to tmp
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    main.UPLOAD_DIR = str(upload_dir)

    client = TestClient(main.app)
    yield client, TestingSessionLocal
    main.app.dependency_overrides.clear()
