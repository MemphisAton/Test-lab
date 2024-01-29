import logging
import os
from dataclasses import dataclass

from environs import Env

logging.basicConfig(level=logging.INFO)


@dataclass
class UrlConfig:
    DATABASE_URL: str


@dataclass
class Config:
    db: UrlConfig


def load_config(path: str) -> Config:
    env = Env()
    env.read_env(path)

    # Проверяем, установлена ли переменная среды IN_DOCKER
    if os.getenv("IN_DOCKER") == '1':
        database_url = env('DOCKER_DATABASE_URL')
        logging.info(f"Using Docker database URL: {database_url}")
    else:
        database_url = env('LOCAL_DATABASE_URL')
        logging.info(f"Using local database URL: {database_url}")

    return Config(db=UrlConfig(DATABASE_URL=database_url))
