"""Запуск учебного HTTP-сервера с MongoDB."""
from pymongo import MongoClient

from conf import settings
from tegugotchi.backend.database.pet_repository import PetRepository
from tegugotchi.backend.server.app import create_app


def main() -> None:
    with MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000) as client:
        repository = PetRepository(client[settings.MONGO_DB_NAME])
        app = create_app(repository)
        # Репозиторий использует read-modify-write: учебный сервер обрабатывает
        # запросы последовательно. Несколько worker-процессов не поддерживаются.
        app.run(
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            threaded=False,
        )


if __name__ == "__main__":
    main()
