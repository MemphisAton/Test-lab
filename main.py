import logging
from typing import List
from uuid import UUID

from fastapi import FastAPI, status
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

import crud
import database
import models
import schemas
from database import SessionLocal
from database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
api_router = APIRouter(prefix="/api/v1")
app.include_router(api_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MENU
@api_router.get("/menus/{menu_id}", response_model=schemas.Menu)
def read_menu(menu_id: UUID, db: Session = Depends(get_db)):
    """
    Получает информацию о конкретном меню по его UUID.

    Args:
    menu_id (UUID): UUID меню.
    db (Session): Сессия базы данных.

    Returns:
    schemas.Menu: Данные о меню, если оно найдено. Иначе возникает исключение HTTPException.
    """
    db_menu = crud.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return db_menu


@api_router.get("/menus", response_model=List[schemas.Menu])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получает список меню, с опциональной пагинацией.

    Args:
    skip (int): Количество пропускаемых записей для пагинации.
    limit (int): Максимальное количество записей, возвращаемых запросом.
    db (Session): Сессия базы данных.

    Returns:
    List[schemas.Menu]: Список объектов меню.
    """
    menus = crud.get_menus(db, skip=skip, limit=limit)
    return [schemas.Menu(
        id=menu.id,
        title=menu.title,
        description=menu.description,
        submenus_count=submenus_count,
        dishes_count=dishes_count
    ) for menu, submenus_count, dishes_count in menus]


@api_router.post("/menus", response_model=schemas.Menu, status_code=status.HTTP_201_CREATED)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    """
    Создает новое меню.

    Args:
    menu (schemas.MenuCreate): Данные для создания нового меню.
    db (Session): Сессия базы данных.

    Returns:
    schemas.Menu: Данные созданного меню.
    """
    new_menu = crud.create_menu(db=db, menu=menu)
    return new_menu


@api_router.patch("/menus/{menu_id}", response_model=schemas.Menu)
def update_menu(menu_id: UUID, menu_data: schemas.MenuUpdate, db: Session = Depends(get_db)):
    """
    Обновляет информацию о меню по его UUID.

    Args:
    menu_id (UUID): UUID меню, которое необходимо обновить.
    menu_data (schemas.MenuUpdate): Обновленные данные для меню.
    db (Session): Сессия базы данных.

    Returns:
    schemas.Menu: Обновленные данные о меню, если оно найдено. Иначе возникает исключение HTTPException.
    """
    db_menu = crud.update_menu(db, menu_id=menu_id, menu_data=menu_data)
    if db_menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return db_menu


@api_router.delete("/menus/{menu_id}")
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    """
    Удаляет меню по его UUID.

    Args:
    menu_id (UUID): UUID меню, которое необходимо удалить.
    db (Session): Сессия базы данных.

    Returns:
    dict: Сообщение об успешном удалении, если меню найдено. Иначе возникает исключение HTTPException.
    """
    if not crud.delete_menu(db=db, menu_id=menu_id):
        raise HTTPException(status_code=404, detail="menu not found")
    return {"message": "Menu deleted"}


# SUBMENU
@api_router.get("/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubMenu)
def read_specific_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    """
    Получает информацию о конкретном подменю в рамках указанного меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю.
    db (Session): Сессия базы данных.

    Returns:
    schemas.SubMenu: Данные о подменю, если оно найдено. Иначе возникает исключение HTTPException.
    """
    submenu = crud.get_specific_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    return submenu


@api_router.get("/menus/{menu_id}/submenus", response_model=List[schemas.SubMenu])
def read_submenus(menu_id: UUID, db: Session = Depends(get_db)):
    """
    Получает список подменю в рамках указанного меню.

    Args:
    menu_id (UUID): UUID меню.
    db (Session): Сессия базы данных.

    Returns:
    List[schemas.SubMenu]: Список подменю.
    """
    submenus = crud.get_submenus_by_menu(db, menu_id=menu_id)
    if submenus is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return submenus


@api_router.post("/menus/{menu_id}/submenus", response_model=schemas.SubMenu, status_code=status.HTTP_201_CREATED)
def create_submenu_for_menu(menu_id: UUID, submenu: schemas.SubMenuCreate, db: Session = Depends(database.get_db)):
    """
    Создает новое подменю в рамках указанного меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu (schemas.SubMenuCreate): Данные для создания нового подменю.
    db (Session): Сессия базы данных.

    Returns:
    schemas.SubMenu: Данные созданного подменю.
    """
    if not crud.get_menu(db, menu_id=menu_id):
        raise HTTPException(status_code=404, detail="menu not found")
    return crud.create_submenu(db=db, submenu=submenu, menu_id=menu_id)


@api_router.patch("/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubMenu)
def update_submenu(menu_id: UUID, submenu_id: UUID, submenu_data: schemas.SubMenuUpdate, db: Session = Depends(get_db)):
    """
    Обновляет подменю в рамках указанного меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю для обновления.
    submenu_data (schemas.SubMenuUpdate): Обновленные данные для подменю.
    db (Session): Сессия базы данных.

    Returns:
    schemas.SubMenu: Обновленные данные о подменю, если оно найдено. Иначе возникает исключение HTTPException.
    """
    updated_submenu = crud.update_submenu(db, menu_id=menu_id, submenu_id=submenu_id, submenu=submenu_data)
    if updated_submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    return updated_submenu


@api_router.delete("/menus/{menu_id}/submenus/{submenu_id}")
def delete_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    """
    Удаляет подменю по его UUID в рамках указанного меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю, которое нужно удалить.
    db (Session): Сессия базы данных.

    Returns:
    dict: Сообщение об успешном удалении, если подменю найдено. Иначе возникает исключение HTTPException.
    """
    if not crud.delete_submenu(db, menu_id=menu_id, submenu_id=submenu_id):
        raise HTTPException(status_code=404, detail="submenu not found")
    return {"message": "SubMenu deleted"}


# DISH
@api_router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=List[schemas.Dish])
def read_dishes(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    """
    Получает список блюд в рамках указанного подменю и меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю.
    db (Session): Сессия базы данных.

    Returns:
    List[schemas.Dish]: Список блюд в подменю.
    """
    dishes = crud.get_dishes_by_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    return dishes


@api_router.post("/menus/{menu_id}/submenus/{submenu_id}/dishes", response_model=schemas.Dish,
                 status_code=status.HTTP_201_CREATED)
def create_dish_for_submenu(menu_id: UUID, submenu_id: UUID, dish: schemas.DishCreate, db: Session = Depends(get_db)):
    """
    Создает новое блюдо в рамках указанного подменю и меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю.
    dish (schemas.DishCreate): Данные для создания нового блюда.
    db (Session): Сессия базы данных.

    Returns:
    schemas.Dish: Данные созданного блюда.
    """
    if not crud.get_specific_submenu(db, menu_id=menu_id, submenu_id=submenu_id):
        raise HTTPException(status_code=404, detail="submenu not found")
    return crud.create_dish(db=db, dish=dish, submenu_id=submenu_id)


@api_router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
def read_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    """
    Получает информацию о конкретном блюде в рамках указанного подменю и меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю.
    dish_id (UUID): UUID блюда.
    db (Session): Сессия базы данных.

    Returns:
    schemas.Dish: Информация о блюде, если оно найдено. Иначе возникает исключение HTTPException.
    """
    db_dish = crud.get_specific_dish(db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")
    return db_dish


@api_router.patch("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", response_model=schemas.Dish)
def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_update: schemas.DishUpdate,
                db: Session = Depends(get_db)):
    """
    Обновляет информацию о блюде в рамках указанного подменю и меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю.
    dish_id (UUID): UUID блюда, которое нужно обновить.
    dish_update (schemas.DishUpdate): Обновленные данные для блюда.
    db (Session): Сессия базы данных.

    Returns:
    schemas.Dish: Обновленные данные о блюде, если оно найдено. Иначе возникает исключение HTTPException.
    """
    db_dish = crud.get_specific_dish(db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail="dish not found")

    updated_dish = crud.update_dish(db, dish_id, dish_update)
    return updated_dish


@api_router.delete("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    """
    Удаляет блюдо по его UUID в рамках указанного подменю и меню.

    Args:
    menu_id (UUID): UUID родительского меню.
    submenu_id (UUID): UUID подменю.
    dish_id (UUID): UUID блюда, которое нужно удалить.
    db (Session): Сессия базы данных.

    Returns:
    dict: Сообщение об успешном удалении, если блюдо найдено. Иначе возникает исключение HTTPException.
    """
    if not crud.delete_dish(db, dish_id=dish_id):
        raise HTTPException(status_code=404, detail="dish not found")
    return {"message": "Dish deleted successfully"}


app.include_router(api_router)
