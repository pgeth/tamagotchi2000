"""Общие настройки тестов.

Для тестов API запускается настоящий HTTP-сервер, но вместо MongoDB
в нём работает mongomock, поэтому ни реальная база, ни ручной запуск
`python main.py` не нужны.
"""
import threading

import mongomock
import pytest
import requests
from werkzeug.serving import make_server

from tegugotchi.backend.database.repository import PetRepository
from tegugotchi.backend.server.app import create_app


@pytest.fixture
def database():
    """Пустая «MongoDB» в памяти. Для каждого теста своя."""
    return mongomock.MongoClient()["tegugotchi_test"]


@pytest.fixture
def repository(database) -> PetRepository:
    return PetRepository(database)


class ApiClient(requests.Session):
    """requests.Session, который сам добавляет адрес сервера к путям."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        return super().request(method, self.base_url + url, *args, **kwargs)


@pytest.fixture(scope="session")
def api():
    """Клиент для запросов к тестовому серверу (на свободном порту)."""
    repository = PetRepository(mongomock.MongoClient()["tegugotchi_test"])
    server = make_server("localhost", 0, create_app(repository))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = ApiClient(f"http://localhost:{server.server_port}")
    yield client
    client.close()
    server.shutdown()
    thread.join()