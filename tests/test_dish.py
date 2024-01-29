from fastapi.testclient import TestClient

from main import app
from models import Menu, SubMenu, Dish

client = TestClient(app)


def test_create_dish(db_session, client):
    '''
    Проверяет, что создание нового блюда в подменю происходит корректно и возвращает информацию о созданном блюде.
    '''
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    test_submenu = SubMenu(title="Test Submenu", description="Test description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    dish_data = {"title": "Test Dish", "description": "Test description", "price": "9.99"}

    response = client.post(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes", json=dish_data)

    assert response.status_code == 201
    created_dish = response.json()
    assert created_dish["title"] == dish_data["title"]


def test_get_specific_dish(db_session, client):
    '''
    Проверяет, что запрос информации о конкретном блюде возвращает корректные данные блюда.
    '''
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    test_submenu = SubMenu(title="Test Submenu", description="Test description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    test_dish = Dish(title="Test Dish", description="Test description", price="9.99", submenu_id=test_submenu.id)
    db_session.add(test_dish)
    db_session.commit()

    response = client.get(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/{test_dish.id}")

    assert response.status_code == 200
    dish_info = response.json()
    assert dish_info["id"] == str(test_dish.id)


def test_update_dish(db_session, client):
    '''
    Проверяет, что обновление данных блюда в подменю работает корректно и возвращает обновленную информацию.
    '''
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    test_submenu = SubMenu(title="Test Submenu", description="Test description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    test_dish = Dish(title="Test Dish", description="Test description", price="9.99", submenu_id=test_submenu.id)
    db_session.add(test_dish)
    db_session.commit()

    update_data = {"title": "Updated Dish", "description": "Updated description", "price": "10.99"}

    response = client.patch(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/{test_dish.id}",
                            json=update_data)

    assert response.status_code == 200
    updated_dish_info = response.json()
    assert updated_dish_info["title"] == update_data["title"]


def test_delete_dish(db_session, client):
    '''
    Проверяет, что удаление блюда из подменю происходит успешно и блюдо отсутствует в базе данных после удаления.
    '''
    test_menu = Menu(title="Parent Menu", description="Parent menu description")
    db_session.add(test_menu)
    db_session.commit()

    test_submenu = SubMenu(title="Test Submenu", description="Test description", menu_id=test_menu.id)
    db_session.add(test_submenu)
    db_session.commit()

    test_dish = Dish(title="Test Dish", description="Test description", price="9.99", submenu_id=test_submenu.id)
    db_session.add(test_dish)
    db_session.commit()

    response = client.delete(f"/api/v1/menus/{test_menu.id}/submenus/{test_submenu.id}/dishes/{test_dish.id}")

    assert response.status_code == 200
    assert db_session.query(Dish).filter(Dish.id == test_dish.id).first() is None
