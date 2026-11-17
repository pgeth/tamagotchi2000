import pytest
 
from tegugotchi.backend.pet import Pet
 
 
@pytest.fixture
def pet() -> Pet:
    return Pet("Жма", 10)
 
 
def test_initial_state(pet):
    assert pet.name == "Жма"
    assert pet.hp == 10
    assert pet.happiness == 2
    assert pet.hunger == 2
    assert pet.hunger_penalty_count == 0
    assert pet.is_alive
 
 
@pytest.mark.parametrize("hp", [0, -5])
def test_init_invalid_hp(hp):
    with pytest.raises(ValueError):
        Pet("Жма", hp)
 
 
def test_feed(pet):
    pet.feed()
    assert (pet.happiness, pet.hunger) == (2, 0)
 
 
def test_feed_hunger_not_negative(pet):
    pet.feed()
    pet.feed()
    assert pet.hunger == 0
 
 
def test_pat(pet):
    pet.pat()
    assert (pet.happiness, pet.hunger) == (3, 3)
 
 
def test_treat(pet):
    pet.treat()
    assert (pet.happiness, pet.hunger) == (4, 1)
 
 
def test_walk(pet):
    pet.walk()
    assert (pet.happiness, pet.hunger) == (3, 5)
    assert pet.hp == 10
 
 
def test_ignore(pet):
    pet.ignore()
    assert (pet.happiness, pet.hunger) == (1, 3)
 
 
def test_hp_lost_when_hunger_above_limit(pet):
    pet.walk()  # голод 5
    pet.pat()  # голод 6
    assert pet.hp == 9
    assert pet.hunger_penalty_count == 1
 
 
def test_penalty_grows_on_consecutive_actions(pet):
    pet.walk()
    pet.pat()  # -1
    pet.pat()  # -2
    pet.pat()  # -3
    assert pet.hp == 10 - 1 - 2 - 3
    assert pet.hunger_penalty_count == 3
 
 
def test_penalty_resets_after_normal_hunger(pet):
    pet.walk()
    pet.pat()  # -1
    pet.feed()  # голод 4
    assert pet.hunger_penalty_count == 0
    pet.walk()  # голод 7, снова -1
    assert pet.hp == 8
 
 
def test_disappears_when_hp_zero():
    pet = Pet("Жма", 1)
    pet.walk()
    pet.pat()  # голод 6, hp 0
    assert not pet.is_alive
 
 
def test_disappears_when_happiness_zero(pet):
    pet.ignore()
    pet.ignore()
    assert not pet.is_alive
 
 
def test_hunger_not_changed_after_disappearing_from_happiness():
    pet = Pet("Жма", 10, happiness=1)
    pet.ignore()  # счастье 0, питомец исчез, голод не меняется
    assert not pet.is_alive
    with pytest.raises(ValueError):
        _ = pet.hunger
 
 
def test_disappeared_manually(pet):
    pet.disappeared()
    assert not pet.is_alive
 
 
def test_disappeared_twice_raises(pet):
    pet.disappeared()
    with pytest.raises(ValueError):
        pet.disappeared()
 
 
@pytest.mark.parametrize("action", ["feed", "pat", "treat", "walk", "ignore"])
def test_actions_on_gone_pet_raise(pet, action):
    pet.disappeared()
    with pytest.raises(ValueError):
        getattr(pet, action)()
 
 
@pytest.mark.parametrize(
    "attr", ["hp", "name", "happiness", "hunger", "hunger_penalty_count"]
)
def test_properties_on_gone_pet_raise(pet, attr):
    pet.disappeared()
    with pytest.raises(ValueError):
        getattr(pet, attr)
 
 
def test_is_alive_available_on_gone_pet(pet):
    pet.disappeared()
    assert pet.is_alive is False
 
 
def test_change_hp_ignored_on_gone_pet(pet):
    pet.disappeared()
    pet._Pet__change_hp(-1)
    assert not pet.is_alive
 
 
def test_change_happiness_ignored_on_gone_pet(pet):
    pet.disappeared()
    pet._Pet__change_happiness(-1)
    assert not pet.is_alive