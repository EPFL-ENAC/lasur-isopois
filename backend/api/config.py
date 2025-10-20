from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):

    API_KEYS: str

    LASUR_WS_URL: str = "https://lasur-ws-dev.epfl.ch"
    LASUR_WS_API_KEY: str = "x5xmBCHGiatVEgagxuyn9ZEuG1TObil6zH38avBJgGg1DJrFZEpnD5iC7FXmYDGN"

    CLIENT_ID_ROME: str = ""
    CLIENT_SECRET_ROME: str = ""
    CLIENT_ID_JOBS: str = ""
    CLIENT_SECRET_JOBS: str = ""
    DEPARTMENTS: str = '["01", "74"]'


@lru_cache()
def get_config():
    return Config()


config = get_config()
