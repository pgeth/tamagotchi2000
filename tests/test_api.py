"""Тесты REST API.

Сервер запускается автоматически (см. conftest.py), а вместо настоящей
MongoDB используется mongomock.
"""
import pytest


def create_pet(api, name="Барсик", hp=10):
    return api.post("/pets", json={"name": name, "hp": hp})


@pytest.fixture
def pet_id(api) -> int:
    response = create_pet(api)
    assert response.status_code == 201
    return response.json()["id"]


# ---------- создание питомца ----------

def test_create_pet(api):
    response = create_pet(api, "Барсик", 10)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Барсик"
    assert body["hp"] == 10
    assert body["happiness"] == 2
    assert body["hunger"] == 2
    assert isinstance(body["id"], int)


def test_create_pets_get_different_ids(api):
    first = create_pet(api).json()["id"]
    second = create_pet(api).json()["id"]
    assert first != second


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"hp": 10},
        {"name": "Барсик"},
        {"name": "", "hp": 10},
        {"name": "   ", "hp": 10},
        {"name": 123, "hp": 10},
        {"name": "Барсик", "hp": 0},
        {"name": "Барсик", "hp": -5},
        {"name": "Барсик", "hp": "10"},
        {"name": "Барсик", "hp": 1.5},
        {"name": "Барсик", "hp": True},
        {"name": "Барсик", "hp": None},
    ],
)
def test_create_pet_invalid_data(api, payload):
    response = api.post("/pets", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()


def test_create_pet_body_not_json(api):
    response = api.post("/pets", data="не json")
    assert response.status_code == 400


def test_create_pet_body_is_list(api):
    response = api.post("/pets", json=[1, 2, 3])
    assert response.status_code == 400


# ---------- статистика ----------

def test_get_pet(api, pet_id):
    response = api.get(f"/pets/{pet_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": pet_id,
        "name": "Барсик",
        "hp": 10,
        "happiness": 2,
        "hunger": 2,
    }


def test_get_unknown_pet(api):
    response = api.get("/pets/999999")
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
def test_action_changes_stats(api, pet_id, action, happiness, hunger):
    response = api.post(f"/pets/{pet_id}/{action}")
    assert response.status_code == 200
    body = response.json()
    assert body["happiness"] == happiness
    assert body["hunger"] == hunger
    assert body["hp"] == 10


def test_action_is_saved(api, pet_id):
    api.post(f"/pets/{pet_id}/treat")
    response = api.get(f"/pets/{pet_id}")
    assert response.json()["happiness"] == 4
    assert response.json()["hunger"] == 1


def test_hunger_not_below_zero(api, pet_id):
    api.post(f"/pets/{pet_id}/feed")
    response = api.post(f"/pets/{pet_id}/feed")
    assert response.json()["hunger"] == 0


def test_action_on_unknown_pet(api):
    response = api.post("/pets/999999/feed")
    assert response.status_code == 404


def test_unknown_action(api, pet_id):
    response = api.post(f"/pets/{pet_id}/jump")
    assert response.status_code == 404


def test_action_wrong_method(api, pet_id):
    response = api.get(f"/pets/{pet_id}/feed")
    assert response.status_code == 405


# ---------- штраф за голод ----------

def test_hunger_above_limit_costs_hp(api, pet_id):
    api.post(f"/pets/{pet_id}/walk")  # голод 5
    response = api.post(f"/pets/{pet_id}/pat")  # голод 6
    assert response.json()["hp"] == 9


def test_hunger_penalty_grows(api, pet_id):
    api.post(f"/pets/{pet_id}/walk")  # голод 5
    api.post(f"/pets/{pet_id}/pat")  # голод 6, hp 9
    response = api.post(f"/pets/{pet_id}/pat")  # голод 7, hp 7
    assert response.json()["hp"] == 7


def test_hunger_penalty_resets(api, pet_id):
    api.post(f"/pets/{pet_id}/walk")
    api.post(f"/pets/{pet_id}/pat")  # hp 9
    api.post(f"/pets/{pet_id}/feed")  # голод 4
    api.post(f"/pets/{pet_id}/walk")  # голод 7, штраф снова 1
    response = api.get(f"/pets/{pet_id}")
    assert response.json()["hp"] == 8


# ---------- исчезновение ----------

def test_pet_disappears_when_happiness_zero(api, pet_id):
    api.post(f"/pets/{pet_id}/ignore")
    response = api.post(f"/pets/{pet_id}/ignore")
    assert response.status_code == 200
    body = response.json()
    assert body["gone"] is True
    assert body["id"] == pet_id
    assert "Барсик" in body["message"]


def test_pet_disappears_when_hp_zero(api):
    pet_id = create_pet(api, "Мурзик", hp=1).json()["id"]
    api.post(f"/pets/{pet_id}/walk")  # голод 5
    response = api.post(f"/pets/{pet_id}/pat")  # голод 6, hp 0
    assert response.json()["gone"] is True


def test_gone_pet_is_not_found(api, pet_id):
    api.post(f"/pets/{pet_id}/ignore")
    api.post(f"/pets/{pet_id}/ignore")
    assert api.get(f"/pets/{pet_id}").status_code == 404
    assert api.post(f"/pets/{pet_id}/feed").status_code == 404


# ---------- прочее ----------

def test_unknown_url(api):
    response = api.get("/nothing")
    assert response.status_code == 404
    assert "error" in response.json()