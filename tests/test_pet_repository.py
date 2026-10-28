import mongomock
import pytest

from tegugotchi.backend.database.pet_repository import PetRepository
from tegugotchi.backend.pet import Pet


@pytest.fixture
def repo() -> PetRepository:
    return PetRepository(mongomock.MongoClient()["tegugotchi"])

def test_ids_are_sequential_integers(repo):
    assert repo.next_id() == 1
    assert repo.next_id() == 2

def test_add_and_get(repo):
    pet_id = repo.add(Pet("Жма", 10))
    pet = repo.get(pet_id)
    assert isinstance(pet_id, int)
    assert (pet.name, pet.hp, pet.happiness, pet.hunger) == ("Жма", 10, 2, 2)
    assert pet.hunger_penalty_count == 0

def test_add_gives_different_ids(repo):
    assert repo.add(Pet("А", 5)) != repo.add(Pet("Б", 5))

def test_get_unknown_returns_none(repo):
    assert repo.get(999) is None

def test_save_updates_stats(repo):
    pet_id = repo.add(Pet("Жма", 10))
    pet = repo.get(pet_id)
    pet.treat()
    repo.save(pet_id, pet)
    saved = repo.get(pet_id)
    assert (saved.happiness, saved.hunger) == (4, 1)

def test_penalty_counter_is_saved(repo):
    pet_id = repo.add(Pet("Жма", 10))
    pet = repo.get(pet_id)
    pet.walk()
    pet.pat()  # голод 6, hp 9
    repo.save(pet_id, pet)
    saved = repo.get(pet_id)
    assert saved.hp == 9
    assert saved.hunger_penalty_count == 1

def test_save_gone_pet_deletes_document(repo):
    pet_id = repo.add(Pet("Жма", 10))
    pet = repo.get(pet_id)
    pet.ignore()
    pet.ignore()  # счастье 0, питомец исчез
    repo.save(pet_id, pet)
    assert repo.get(pet_id) is None

def test_delete(repo):
    pet_id = repo.add(Pet("Жма", 10))
    repo.delete(pet_id)
    assert repo.get(pet_id) is None

def test_delete_unknown_does_nothing(repo):
    repo.delete(999)
