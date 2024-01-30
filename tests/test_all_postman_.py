def test_menu_and_dishes_workflow(client, db_session):
    # Создаем меню
    menu_data = {"title": "New Test Menu", "description": "A test menu description"}
    response = client.post("/api/v1/menus", json=menu_data)
    assert response.status_code == 201
    menu_id = response.json()["id"]

    # Создаем подменю
    submenu_data = {"title": "New Test Submenu", "description": "A test submenu description"}
    response = client.post(f"/api/v1/menus/{menu_id}/submenus", json=submenu_data)
    assert response.status_code == 201
    submenu_id = response.json()["id"]

    # Создаем блюдо 1
    dish_data = {"title": "New Test Dish 1", "description": "A test dish description", "price": "9.99"}
    response = client.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json=dish_data)
    assert response.status_code == 201
    dish1_id = response.json()["id"]

    # Создаем блюдо 2
    dish_data = {"title": "New Test Dish 2", "description": "Another test dish description", "price": "12.99"}
    response = client.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json=dish_data)
    assert response.status_code == 201
    dish2_id = response.json()["id"]

    # Получаем информацию о блюде 1
    response = client.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish1_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "New Test Dish 1"

    # Удаляем подменю
    response = client.delete(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}")
    assert response.status_code == 200

    # Получаем список меню и проверяем, что подменю удалено
    response = client.get(f"/api/v1/menus/{menu_id}/details")
    assert response.status_code == 200
    assert response.json()["submenus_count"] == 0

    # Удаляем меню
    response = client.delete(f"/api/v1/menus/{menu_id}")
    assert response.status_code == 200
