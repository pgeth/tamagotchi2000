from pymongo import MongoClient
 
from conf import settings
from tegugotchi.backend.database.repository import PetRepository
from tegugotchi.backend.server.app import create_app
 
 
def main() -> None:
    client = MongoClient(settings.MONGO_URI)
    repository = PetRepository(client[settings.MONGO_DB_NAME])
    app = create_app(repository)
    app.run(host=settings.SERVER_HOST, port=settings.SERVER_PORT)
 
 
if __name__ == "__main__":
    main()