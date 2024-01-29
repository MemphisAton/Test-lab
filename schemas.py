from uuid import UUID

from pydantic import BaseModel


# MENU
class Menu(BaseModel):
    id: UUID
    title: str
    description: str
    submenus_count: int = None
    dishes_count: int = None


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuDetails(BaseModel):
    id: UUID
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuUpdate(BaseModel):
    title: str
    description: str


# SUBMENU
class SubMenu(BaseModel):
    id: UUID
    title: str
    description: str
    dishes_count: int = None


class SubMenuCreate(BaseModel):
    title: str
    description: str


class SubMenuUpdate(BaseModel):
    title: str
    description: str


# DISH
class Dish(BaseModel):
    id: UUID
    title: str
    description: str
    price: str


class DishCreate(BaseModel):
    title: str
    description: str
    price: str


class DishUpdate(BaseModel):
    title: str
    description: str
    price: str
