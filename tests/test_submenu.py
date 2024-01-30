from fastapi.testclient import TestClient

from main import app
from models import Menu, SubMenu

client = TestClient(app)


def test_create_submenu(db_session, client):
    """
    Тестирует создание подменю. Создает родительское меню и подменю, затем отправляет запрос на создание подменю.
    Проверяет, что запрос возвращает статус 201 и содержит идентификатор созданного подменю.
    """
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    submenu_data = {"title": "Test Submenu", "description": "Test description"}
    response = client.post(f"/api/v1/menus/{test_menu.id}/submenus", json=submenu_data)

    assert response.status_code == 201
    assert "id" in response.json()


def test_get_specific_submenu(db_session, client):
    """
    Тестирует получение информации о конкретном подменю. Создает тестовые данные для меню и подменю,
    затем отправляет запрос на получение информации о подменю.
    Проверяет, что запрос возвращает статус 200 и корректные данные о подменю.
    """
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    test_submenu = SubMenu(title="Test Submenu", description="Test description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    response = client.get(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}")

    assert response.status_code == 200
    submenu_response = response.json()
    assert submenu_response["id"] == str(test_submenu.id)
    assert submenu_response["title"] == "Test Submenu"
    assert submenu_response["description"] == "Test description"


def test_update_submenu(db_session, client):
    """
    Тестирует обновление подменю. Создает тестовые данные для меню и подменю,
    затем отправляет запрос на обновление подменю с новыми данными.
    Проверяет, что запрос возвращает статус 200 и обновленные данные подменю.
    """
    test_menu = db_session.query(Menu).first()  # Получаем первое меню из базы данных
    assert test_menu is not None, "Test menu should exist"

    test_submenu = SubMenu(title="Test Submenu", description="Test Submenu Description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    assert test_submenu is not None, "Test submenu should exist"

    update_data = {"title": "Updated Test Submenu", "description": "Updated Description"}

    response = client.patch(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}", json=update_data)

    assert response.status_code == 200, "Response status should be 200"
    db_session.refresh(test_submenu)

    updated_submenu = response.json()
    assert updated_submenu["title"] == "Updated Test Submenu", "Submenu title should be updated"
    assert updated_submenu["description"] == "Updated Description", "Submenu description should be updated"

    db_updated_submenu = db_session.query(SubMenu).filter(SubMenu.id == test_submenu.id).first()
    assert db_updated_submenu.title == "Updated Test Submenu", "Database submenu title should be updated"
    assert db_updated_submenu.description == "Updated Description", "Database submenu description should be updated"


def test_delete_submenu(db_session, client):
    """
    Тестирует удаление подменю. Создает тестовые данные для меню и подменю,
    затем отправляет запрос на удаление подменю.
    Проверяет, что запрос возвращает статус 200 и подменю удалено из базы данных.
    """
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    test_submenu = SubMenu(title="Test Submenu", description="Test description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    assert db_session.query(SubMenu).filter(SubMenu.id == test_submenu.id).first() is not None, "Submenu should exist"

    response = client.delete(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}")

    assert response.status_code == 200, "Response status should be 200"

    assert db_session.query(SubMenu).filter(SubMenu.id == test_submenu.id).first() is None, "Submenu should be deleted"
