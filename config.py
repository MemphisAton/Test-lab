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

    # Проверяем, запущены ли тесты в Docker
    if os.getenv("IN_DOCKER") == '1' and os.getenv("RUNNING_TESTS") == '1':
        database_url = env('DOCKER_DATABASE_TEST_URL')
        logging.info("Using Docker database URL for tests: {}".format(database_url))
    # Проверяем, запущено ли приложение в Docker
    elif os.getenv("IN_DOCKER") == '1':
        database_url = env('DOCKER_DATABASE_URL')
        logging.info("Using Docker database URL: {}".format(database_url))
    else:
        database_url = env('LOCAL_DATABASE_URL')
        logging.info("Using local database URL: {}".format(database_url))

    return Config(db=UrlConfig(DATABASE_URL=database_url))
