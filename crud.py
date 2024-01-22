from uuid import UUID

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

import models
import schemas


# CRUD FOR MENU
def get_menu(db: Session, menu_id: UUID) -> dict:
    """
    Получение информации о конкретном меню по его ID.
    Включает в себя подсчет количества подменю и блюд.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Уникальный идентификатор меню.

    Returns:
    dict: Словарь с данными меню или None, если меню не найдено.
    """
    menu_info = (
        db.query(
            models.Menu,
            func.count(distinct(models.SubMenu.id)).label("submenus_count"),
            func.coalesce(func.count(models.Dish.id), 0).label("dishes_count")
        )
        .outerjoin(models.SubMenu, models.Menu.id == models.SubMenu.menu_id)
        .outerjoin(models.Dish, models.SubMenu.id == models.Dish.submenu_id)
        .filter(models.Menu.id == menu_id)
        .group_by(models.Menu.id)
        .first()
    )
    if menu_info:
        menu_dict = menu_info[0].__dict__
        menu_dict.pop("_sa_instance_state", None)
        menu_dict["submenus_count"] = menu_info.submenus_count
        menu_dict["dishes_count"] = menu_info.dishes_count

        return menu_dict
    else:
        return None


def get_menus(db: Session, skip: int = 0, limit: int = 100):
    """
    Получение списка меню с информацией о количестве подменю и блюд для каждого меню.
    Поддерживает пагинацию через параметры skip и limit.

    Args:
    db (Session): Сессия базы данных.
    skip (int): Количество пропускаемых записей.
    limit (int): Максимальное количество записей для возврата.

    Returns:
    list: Список меню с дополнительной информацией.
    """
    results = (
        db.query(
            models.Menu,
            func.coalesce(func.count(models.SubMenu.id), 0).label("submenus_count"),
            func.coalesce(func.count(models.Dish.id), 0).label("dishes_count"))
        .outerjoin(models.SubMenu, models.Menu.id == models.SubMenu.menu_id)
        .outerjoin(models.Dish, models.SubMenu.id == models.Dish.submenu_id)
        .group_by(models.Menu.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return results


def create_menu(db: Session, menu: schemas.MenuCreate) -> schemas.Menu:
    """
    Создание нового меню.

    Args:
    db (Session): Сессия базы данных.
    menu (schemas.MenuCreate): Данные для создания нового меню.

    Returns:
    schemas.Menu: Созданный объект меню.
    """
    db_menu = models.Menu(
        title=menu.title,
        description=menu.description, )
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return schemas.Menu(
        id=db_menu.id,
        title=db_menu.title,
        description=db_menu.description,
        submenus_count=0,
        dishes_count=0,
    )


def update_menu(db: Session, menu_id: UUID, menu_data: schemas.MenuUpdate):
    """
    Обновление существующего меню.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Уникальный идентификатор меню для обновления.
    menu_data (schemas.MenuUpdate): Данные для обновления меню.

    Returns:
    Обновленный объект меню или None, если меню не найдено.
    """
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if not db_menu:
        return None
    for var, value in vars(menu_data).items():
        if value is not None:
            setattr(db_menu, var, value)
    db.commit()
    db.refresh(db_menu)
    return db_menu


def delete_menu(db: Session, menu_id: UUID):
    """
    Удаление меню по его идентификатору.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Уникальный идентификатор меню для удаления.

    Returns:
    bool: True, если меню удалено успешно, иначе False.
    """
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu:
        db.delete(db_menu)
        db.commit()
        return True
    return False


# CRUD FOR SUBMENU
def get_specific_submenu(db: Session, menu_id: UUID, submenu_id: UUID):
    """
    Получение информации о конкретном подменю, включая количество блюд в нем.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Идентификатор родительского меню.
    submenu_id (UUID): Идентификатор подменю.

    Returns:
    schemas.SubMenu: Информация о подменю или None, если подменю не найдено.
    """
    submenu_info = (
        db.query(
            models.SubMenu,
            func.count(distinct(models.Dish.id)).label("dishes_count"))
        .outerjoin(models.Dish, models.SubMenu.dishes)
        .filter(models.SubMenu.id == submenu_id, models.SubMenu.menu_id == menu_id)
        .group_by(models.SubMenu.id)
        .first())
    if submenu_info:
        submenu_dict = submenu_info[0].__dict__
        submenu_dict.pop("_sa_instance_state", None)
        submenu_dict["dishes_count"] = submenu_info.dishes_count
        submenu_data = schemas.SubMenu(
            id=submenu_dict["id"],
            title=submenu_dict["title"],
            description=submenu_dict["description"],
            dishes_count=submenu_dict["dishes_count"])
        return submenu_data
    else:
        return None


def get_submenus_by_menu(db: Session, menu_id: UUID):
    """
    Получение всех подменю для конкретного меню.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Идентификатор меню.

    Returns:
    List[models.SubMenu]: Список подменю данного меню.
    """
    return db.query(models.SubMenu).filter(models.SubMenu.menu_id == menu_id).all()


def create_submenu(db: Session, submenu: schemas.SubMenuCreate, menu_id: UUID):
    """
    Создание нового подменю.

    Args:
    db (Session): Сессия базы данных.
    submenu (schemas.SubMenuCreate): Данные для создания подменю.
    menu_id (UUID): Идентификатор родительского меню.

    Returns:
    schemas.SubMenu: Созданный объект подменю.
    """
    db_submenu = models.SubMenu(
        title=submenu.title,
        description=submenu.description,
        menu_id=menu_id
    )
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return schemas.SubMenu(
        id=db_submenu.id,
        title=db_submenu.title,
        description=db_submenu.description,
        dishes_count=0, )


def update_submenu(db: Session, menu_id: UUID, submenu_id: UUID, submenu: schemas.SubMenuUpdate):
    """
    Обновление существующего подменю.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Идентификатор родительского меню.
    submenu_id (UUID): Идентификатор подменю для обновления.
    submenu (schemas.SubMenuUpdate): Данные для обновления подменю.

    Returns:
    Обновленный объект подменю или None, если подменю не найдено.
    """
    db_submenu = db.query(models.SubMenu).filter(models.SubMenu.id == submenu_id,
                                                 models.SubMenu.menu_id == menu_id).first()
    if db_submenu is None:
        return None
    for var, value in vars(submenu).items():
        setattr(db_submenu, var, value) if value else None
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


def delete_submenu(db: Session, menu_id: UUID, submenu_id: UUID):
    """
      Удаление подменю.

      Args:
      db (Session): Сессия базы данных.
      menu_id (UUID): Идентификатор родительского меню.
      submenu_id (UUID): Идентификатор подменю для удаления.

      Returns:
      bool: True, если подменю удалено успешно, иначе False.
      """
    db_submenu = db.query(models.SubMenu).filter(models.SubMenu.id == submenu_id,
                                                 models.SubMenu.menu_id == menu_id).first()
    if db_submenu:
        db.delete(db_submenu)
        db.commit()
        return True
    return False


# CRUD FOR DISH
def get_dishes_by_submenu(db: Session, menu_id: UUID, submenu_id: UUID):
    """
    Получение всех блюд в определенном подменю.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Идентификатор родительского меню.
    submenu_id (UUID): Идентификатор подменю.

    Returns:
    List[models.Dish]: Список блюд в подменю.
    """
    dishes = db.query(models.Dish).join(models.SubMenu).filter(
        models.SubMenu.id == submenu_id,
        models.SubMenu.menu_id == menu_id
    ).all()
    for dish in dishes:
        if dish.price:
            dish.price = f"{float(dish.price):.2f}"
    return dishes


def create_dish(db: Session, dish: schemas.DishCreate, submenu_id: UUID):
    """
    Создает новое блюдо в подменю. Проверяет наличие уже существующего блюда с тем же названием в этом подменю.

    Args:
    db (Session): Сессия базы данных.
    dish (schemas.DishCreate): Данные для создания блюда.
    submenu_id (UUID): Идентификатор подменю, в котором создается блюдо.

    Returns:
    models.Dish: Созданное блюдо.
    """
    existing_dish = db.query(models.Dish).filter(
        models.Dish.title == dish.title,
        models.Dish.submenu_id == submenu_id
    ).first()
    if existing_dish:
        return existing_dish
    new_dish = models.Dish(
        title=dish.title,
        description=dish.description,
        price=dish.price,
        submenu_id=submenu_id)
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    return new_dish


def get_specific_dish(db: Session, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    """
    Получает информацию о конкретном блюде, учитывая идентификаторы меню, подменю и блюда.

    Args:
    db (Session): Сессия базы данных.
    menu_id (UUID): Идентификатор меню.
    submenu_id (UUID): Идентификатор подменю.
    dish_id (UUID): Идентификатор блюда.

    Returns:
    models.Dish: Информация о блюде.
    """
    dish = db.query(models.Dish).join(
        models.SubMenu, models.SubMenu.id == models.Dish.submenu_id
    ).filter(
        models.Dish.id == dish_id,
        models.SubMenu.id == submenu_id,
        models.SubMenu.menu_id == menu_id
    ).first()
    if dish and dish.price:
        dish.price = f"{float(dish.price):.2f}"

    return dish


def update_dish(db: Session, dish_id: UUID, dish_update: schemas.DishUpdate):
    """
    Обновляет информацию о блюде по его идентификатору.

    Args:
    db (Session): Сессия базы данных.
    dish_id (UUID): Идентификатор блюда для обновления.
    dish_update (schemas.DishUpdate): Обновленные данные блюда.

    Returns:
    models.Dish: Обновленная информация о блюде.
    """
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if db_dish is None:
        return None
    for var, value in vars(dish_update).items():
        setattr(db_dish, var, value) if value is not None else None
    db.commit()
    db.refresh(db_dish)
    return db_dish


def delete_dish(db: Session, dish_id: UUID) -> bool:
    """
    Удаляет блюдо по его идентификатору.

    Args:
    db (Session): Сессия базы данных.
    dish_id (UUID): Идентификатор блюда для удаления.

    Returns:
    bool: True, если удаление успешно, иначе False.
    """
    dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if dish:
        db.delete(dish)
        db.commit()
        return True
    return False
