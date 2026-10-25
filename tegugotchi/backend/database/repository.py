"""Хранение питомцев в MongoDB."""
from pymongo import ReturnDocument
from pymongo.database import Database

from tegugotchi.backend.pet import Pet


class PetRepository:
    """Сохраняет и загружает питомцев.

    Принимает готовую базу данных, поэтому в тестах вместо настоящей
    MongoDB можно передать mongomock.
    """

    def __init__(self, database: Database) -> None:
        self._pets = database["pets"]
        self._counters = database["counters"]

    def _next_id(self) -> int:
        """Следующий свободный номер питомца (1, 2, 3, ...)."""
        counter = self._counters.find_one_and_update(
            {"_id": "pets"},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return counter["value"]

    @staticmethod
    def _to_document(pet: Pet) -> dict:
        return {
            "name": pet.name,
            "hp": pet.hp,
            "happiness": pet.happiness,
            "hunger": pet.hunger,
            "hunger_penalty_count": pet.hunger_penalty_count,
        }

    def create(self, pet: Pet) -> int:
        """Сохранить нового питомца и вернуть его номер."""
        pet_id = self._next_id()
        self._pets.insert_one({"_id": pet_id, **self._to_document(pet)})
        return pet_id

    def get(self, pet_id: int) -> Pet | None:
        """Загрузить питомца. Если такого нет, вернёт None."""
        document = self._pets.find_one({"_id": pet_id})
        if document is None:
            return None
        return Pet(
            name=document["name"],
            hp=document["hp"],
            happiness=document["happiness"],
            hunger=document["hunger"],
            hunger_penalty_count=document["hunger_penalty_count"],
        )

    def save(self, pet_id: int, pet: Pet) -> None:
        """Записать новое состояние живого питомца."""
        self._pets.update_one(
            {"_id": pet_id}, {"$set": self._to_document(pet)}
        )

    def delete(self, pet_id: int) -> None:
        """Удалить питомца (он исчез)."""
        self._pets.delete_one({"_id": pet_id})