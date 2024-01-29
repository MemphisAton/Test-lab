from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models import Menu, SubMenu, Dish

client = TestClient(app)


def test_get_menu_not_found():
    '''
    Проверяет, что при запросе несуществующего меню API возвращает статус код 404.
    '''
    non_existing_menu_id = uuid4()
    response = client.get(f"/api/v1/menus/{non_existing_menu_id}")
    assert response.status_code == 404


def test_get_menu(db_session, create_test_menu):
    '''
    Проверяет, что при запросе существующего меню API возвращает статус код 200 и содержит информацию о меню.
    '''
    test_menu = create_test_menu
    response = client.get(f"/api/v1/menus/{test_menu.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(test_menu.id)


def test_get_menus_pagination():
    '''
    Проверяет работу пагинации, убеждаясь, что количество элементов в ответе соответствует указанному лимиту.
    '''
    response = client.get("/api/v1/menus?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) <= 10


def test_create_menu():
    '''
    Проверяет, что создание нового меню работает корректно и возвращает идентификатор нового меню.
    '''
    menu_data = {"title": "Test Menu", "description": "Test Description"}
    response = client.post("/api/v1/menus", json=menu_data)  # Исправленный URL
    assert response.status_code == 201
    assert "id" in response.json()


def test_update_menu(db_session, client):
    """
    Тестирует, что обновление меню происходит корректно.
    Проверяет, что обновленное меню возвращается в ответе.
    """
    test_menu = db_session.query(Menu).first()

    assert test_menu is not None

    update_data = {"title": "Updated Test Menu", "description": "Updated Description"}

    response = client.patch(f"/api/v1/menus/{test_menu.id}", json=update_data)

    assert response.status_code == 200
    db_session.refresh(test_menu)
    updated_menu = response.json()
    assert updated_menu["title"] == "Updated Test Menu"
    assert updated_menu["description"] == "Updated Description"

    db_updated_menu = db_session.query(Menu).filter(Menu.id == test_menu.id).first()
    assert db_updated_menu.title == "Updated Test Menu"
    assert db_updated_menu.description == "Updated Description"


def test_delete_menu(create_test_menu):
    '''
    Проверяет, что удаление меню работает корректно и возвращает статус 200 при успешном удалении.
    '''
    test_menu = create_test_menu
    response = client.delete(f"/api/v1/menus/{test_menu.id}")
    assert response.status_code == 200


@pytest.fixture
def test_data(db_session: Session):
    """
    Подготавливает тестовые данные: меню, подменю и блюда для последующего использования в тестах.
    """
    menu = Menu(title="Test Menu", description="A test menu for details")
    db_session.add(menu)
    db_session.commit()

    submenu1 = SubMenu(title="Test Submenu 1", menu_id=menu.id)
    submenu2 = SubMenu(title="Test Submenu 2", menu_id=menu.id)
    db_session.add(submenu1)
    db_session.add(submenu2)
    db_session.commit()

    dish1 = Dish(title="Test Dish 1", price=10, submenu_id=submenu1.id)
    dish2 = Dish(title="Test Dish 2", price=12, submenu_id=submenu2.id)
    dish3 = Dish(title="Test Dish 3", price=15, submenu_id=submenu2.id)
    db_session.add(dish1)
    db_session.add(dish2)
    db_session.add(dish3)
    db_session.commit()

    return {
        "menu_id": menu.id,
        "submenus_count": 2,
        "dishes_count": 3,
    }


def test_read_menu_details(test_data):
    """
    Тестирует получение детальной информации о меню, включая количество подменю и блюд.
    """
    response = client.get(f"/api/v1/menus/{test_data['menu_id']}/details")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(test_data["menu_id"])
    assert data["submenus_count"] == test_data["submenus_count"]
    assert data["dishes_count"] == test_data["dishes_count"]


def test_read_menu_details_not_found():
    """
    Проверяет, что запрос деталей несуществующего меню возвращает статус 404.
    """
    response = client.get(f"/api/v1/menus/{uuid4()}/details")

    assert response.status_code == 404
