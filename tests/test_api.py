"""Тесты REST API. Ожидают, что сервер запущен на http://localhost:8008."""
import pytest
import requests

BASE_URL = "http://localhost:8008"


def create_pet(name="Жма", hp=10):
    return requests.post(f"{BASE_URL}/pets", json={"name": name, "hp": hp})


@pytest.fixture
def pet_id() -> int:
    response = create_pet()
    assert response.status_code == 201
    return response.json()["id"]


# ---------- создание питомца ----------

def test_create_pet():
    response = create_pet("Жма", 10)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Жма"
    assert body["hp"] == 10
    assert body["happiness"] == 2
    assert body["hunger"] == 2
    assert isinstance(body["id"], int)


def test_create_pets_get_different_ids():
    first = create_pet().json()["id"]
    second = create_pet().json()["id"]
    assert first != second


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"hp": 10},
        {"name": "Жма"},
        {"name": "", "hp": 10},
        {"name": "   ", "hp": 10},
        {"name": 123, "hp": 10},
        {"name": "Жма", "hp": 0},
        {"name": "Жма", "hp": -5},
        {"name": "Жма", "hp": "10"},
        {"name": "Жма", "hp": 1.5},
        {"name": "Жма", "hp": True},
        {"name": "Жма", "hp": None},
    ],
)
def test_create_pet_invalid_data(payload):
    response = requests.post(f"{BASE_URL}/pets", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_create_pet_body_not_json():
    response = requests.post(f"{BASE_URL}/pets", data="не json")
    assert response.status_code == 400


def test_create_pet_body_is_list():
    response = requests.post(f"{BASE_URL}/pets", json=[1, 2, 3])
    assert response.status_code == 400


# ---------- статистика ----------

def test_get_pet(pet_id):
    response = requests.get(f"{BASE_URL}/pets/{pet_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": pet_id,
        "name": "Жма",
        "hp": 10,
        "happiness": 2,
        "hunger": 2,
    }


def test_get_unknown_pet():
    response = requests.get(f"{BASE_URL}/pets/999999")
    assert response.status_code == 404
    assert response.json() == {"error": "pet not found"}


# ---------- действия ----------

@pytest.mark.parametrize(
    "action, happiness, hunger",
    [
        ("feed", 2, 0),
        ("pat", 3, 3),
        ("treat", 4, 1),
        ("walk", 3, 5),
        ("ignore", 1, 3),
    ],
)
def test_action_changes_stats(pet_id, action, happiness, hunger):
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/{action}")
    assert response.status_code == 200
    body = response.json()
    assert body["happiness"] == happiness
    assert body["hunger"] == hunger
    assert body["hp"] == 10


def test_action_is_saved(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/treat")
    response = requests.get(f"{BASE_URL}/pets/{pet_id}")
    assert response.json()["happiness"] == 4
    assert response.json()["hunger"] == 1


def test_hunger_not_below_zero(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/feed")
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/feed")
    assert response.json()["hunger"] == 0


def test_action_on_unknown_pet():
    response = requests.post(f"{BASE_URL}/pets/999999/feed")
    assert response.status_code == 404


def test_unknown_action(pet_id):
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/jump")
    assert response.status_code == 404


def test_action_wrong_method(pet_id):
    response = requests.get(f"{BASE_URL}/pets/{pet_id}/feed")
    assert response.status_code == 405


# ---------- штраф за голод ----------

def test_hunger_above_limit_costs_hp(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/walk")  # голод 5
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/pat")  # голод 6
    assert response.json()["hp"] == 9


def test_hunger_penalty_grows(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/walk")  # голод 5
    requests.post(f"{BASE_URL}/pets/{pet_id}/pat")  # голод 6, hp 9
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/pat")  # голод 7, hp 7
    assert response.json()["hp"] == 7


def test_hunger_penalty_resets(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/walk")
    requests.post(f"{BASE_URL}/pets/{pet_id}/pat")  # hp 9
    requests.post(f"{BASE_URL}/pets/{pet_id}/feed")  # голод 4
    requests.post(f"{BASE_URL}/pets/{pet_id}/walk")  # голод 7, штраф снова 1
    response = requests.get(f"{BASE_URL}/pets/{pet_id}")
    assert response.json()["hp"] == 8


# ---------- исчезновение ----------

def test_pet_disappears_when_happiness_zero(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/ignore")
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/ignore")
    assert response.status_code == 200
    body = response.json()
    assert body["gone"] is True
    assert body["id"] == pet_id
    assert "Жма" in body["message"]


def test_pet_disappears_when_hp_zero():
    pet_id = create_pet("Валера", hp=1).json()["id"]
    requests.post(f"{BASE_URL}/pets/{pet_id}/walk")  # голод 5
    response = requests.post(f"{BASE_URL}/pets/{pet_id}/pat")  # голод 6, hp 0
    assert response.json()["gone"] is True


def test_gone_pet_is_not_found(pet_id):
    requests.post(f"{BASE_URL}/pets/{pet_id}/ignore")
    requests.post(f"{BASE_URL}/pets/{pet_id}/ignore")
    assert requests.get(f"{BASE_URL}/pets/{pet_id}").status_code == 404
    assert requests.post(f"{BASE_URL}/pets/{pet_id}/feed").status_code == 404


# ---------- прочее ----------

def test_unknown_url():
    response = requests.get(f"{BASE_URL}/nothing")
    assert response.status_code == 404
    assert "error" in response.json()