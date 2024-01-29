import sys
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIRECTORY))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from starlette.testclient import TestClient
from database import Base, get_db
from main import app
from models import Menu

from config import load_config
config_url = load_config('.env')
TEST_DATABASE_URL = config_url.db.DATABASE_URL


@pytest.fixture(scope="session")
def engine():
    """
    Создает и возвращает движок базы данных для сессии тестирования.
    """
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def tables(engine):
    """
    Создает таблицы перед началом тестирования и удаляет их после окончания.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, tables):
    """
    Создает и возвращает сессию базы данных для каждого теста.
    Добавляет тестовые данные и удаляет их после завершения теста.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    test_menus = [
        Menu(title="Test Menu 1", description="Description for test menu 1"),
        Menu(title="Test Menu 2", description="Description for test menu 2"),
    ]
    session.add_all(test_menus)
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """
    Создает и возвращает тестовый клиент FastAPI.
    Подменяет зависимость базы данных на тестовую сессию базы данных.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def create_test_menu(db_session):
    """
    Создает и возвращает тестовое меню для использования в тестах.
    """
    test_menu = Menu(title="Test Menu", description="A test menu")
    db_session.add(test_menu)
    db_session.commit()
    yield test_menu
