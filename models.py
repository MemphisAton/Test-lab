import uuid

from sqlalchemy import Column, String
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Menu(Base):
    __tablename__ = 'menus'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String)
    description = Column(String)
    submenus = relationship("SubMenu", cascade="all, delete-orphan")


class SubMenu(Base):
    __tablename__ = 'submenus'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, index=True)
    description = Column(String)
    menu_id = Column(UUID, ForeignKey('menus.id'))
    dishes = relationship("Dish", cascade="all, delete-orphan")


class Dish(Base):
    __tablename__ = 'dishes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(String)
    submenu_id = Column(UUID, ForeignKey('submenus.id'))
