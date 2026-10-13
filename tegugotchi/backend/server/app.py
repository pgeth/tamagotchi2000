"""HTTP-сервер виртуального питомца."""
from flask import Flask, jsonify, request

from tegugotchi.backend.pet import Pet

ACTIONS = ("feed", "pat", "treat", "walk", "ignore")


def pet_to_dict(pet_id: int, pet: Pet) -> dict:
    """Статистика живого питомца."""
    return {
        "id": pet_id,
        "name": pet.name,
        "hp": pet.hp,
        "happiness": pet.happiness,
        "hunger": pet.hunger,
    }


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False

    pets: dict[int, Pet] = {}
    counter = {"next_id": 1}

    def error(message: str, status: int):
        return jsonify({"error": message}), status

    @app.post("/pets")
    def create_pet():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error("body must be a JSON object", 400)

        name = data.get("name")
        hp = data.get("hp")
        if not isinstance(name, str) or not name.strip():
            return error("name must be a non-empty string", 400)
        if isinstance(hp, bool) or not isinstance(hp, int):
            return error("hp must be an integer", 400)

        try:
            pet = Pet(name, hp)
        except ValueError as exc:
            return error(str(exc), 400)

        pet_id = counter["next_id"]
        counter["next_id"] += 1
        pets[pet_id] = pet
        return jsonify(pet_to_dict(pet_id, pet)), 201

    @app.get("/pets/<int:pet_id>")
    def get_pet(pet_id: int):
        pet = pets.get(pet_id)
        if pet is None:
            return error("pet not found", 404)
        return jsonify(pet_to_dict(pet_id, pet))

    @app.post("/pets/<int:pet_id>/<action>")
    def do_action(pet_id: int, action: str):
        pet = pets.get(pet_id)
        if pet is None or action not in ACTIONS:
            return error("pet not found", 404)

        name = pet.name  # после исчезновения имя уже не прочитать
        getattr(pet, action)()

        if not pet.is_alive:
            del pets[pet_id]
            return jsonify(
                {"id": pet_id, "gone": True, "message": f"{name} исчез"}
            )
        return jsonify(pet_to_dict(pet_id, pet))

    @app.errorhandler(404)
    def not_found(_):
        return error("not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(_):
        return error("method not allowed", 405)

    return app