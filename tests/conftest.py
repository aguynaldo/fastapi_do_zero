import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi_do_zero.app import app
from fastapi_do_zero.database import get_session
from fastapi_do_zero.models import Base, User
from fastapi_do_zero.security import get_password_hash


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    user = User(
        username='Teste',
        email='teste@teste.com',
        password=get_password_hash('123mudar@'),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = '123mudar@'

    return user
