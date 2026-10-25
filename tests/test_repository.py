import pytest

from tegugotchi.backend.pet import Pet


def test_create_returns_sequential_ids(repository):
    assert repository.create(Pet("Барсик", 10)) == 1
    assert repository.create(Pet("Мурзик", 5)) == 2


def test_get_returns_saved_pet(repository):
    pet_id = repository.create(Pet("Барсик", 10))
    pet = repository.get(pet_id)
    assert pet.name == "Барсик"
    assert pet.hp == 10
    assert pet.happiness == 2
    assert pet.hunger == 2
    assert pet.hunger_penalty_count == 0
    assert pet.is_alive


def test_get_unknown_pet_returns_none(repository):
    assert repository.get(999) is None


def test_save_updates_state(repository):
    pet_id = repository.create(Pet("Барсик", 10))
    pet = repository.get(pet_id)
    pet.walk()
    pet.pat()  # голод 6, штраф за голод
    repository.save(pet_id, pet)

    loaded = repository.get(pet_id)
    assert loaded.hp == 9
    assert loaded.happiness == 4
    assert loaded.hunger == 6
    assert loaded.hunger_penalty_count == 1


def test_penalty_counter_survives_save(repository):
    """Нарастающий штраф за голод не должен сбрасываться между запросами."""
    pet_id = repository.create(Pet("Барсик", 10))
    for action in ("walk", "pat", "pat"):
        pet = repository.get(pet_id)
        getattr(pet, action)()
        repository.save(pet_id, pet)
    assert repository.get(pet_id).hp == 10 - 1 - 2


def test_delete_removes_pet(repository):
    pet_id = repository.create(Pet("Барсик", 10))
    repository.delete(pet_id)
    assert repository.get(pet_id) is None


def test_ids_are_not_reused_after_delete(repository):
    first = repository.create(Pet("Барсик", 10))
    repository.delete(first)
    assert repository.create(Pet("Мурзик", 5)) == first + 1


def test_data_is_stored_in_database(repository, database):
    pet_id = repository.create(Pet("Барсик", 10))
    document = database["pets"].find_one({"_id": pet_id})
    assert document == {
        "_id": pet_id,
        "name": "Барсик",
        "hp": 10,
        "happiness": 2,
        "hunger": 2,
        "hunger_penalty_count": 0,
    }


@pytest.mark.parametrize("action", ["feed", "pat", "treat", "walk", "ignore"])
def test_every_action_roundtrip(repository, action):
    pet_id = repository.create(Pet("Барсик", 10))
    pet = repository.get(pet_id)
    getattr(pet, action)()
    repository.save(pet_id, pet)
    loaded = repository.get(pet_id)
    assert (loaded.happiness, loaded.hunger) == (pet.happiness, pet.hunger)