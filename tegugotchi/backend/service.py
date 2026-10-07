from tegugotchi.backend.pet import Pet

class PetService:
    def __init__(self) -> None:
        self.__pets = {}

    def __stat(self, id : int) -> dict:
        pet = self.__pets[id]
        if pet.is_alive:
            return {
                "name" : pet.name,
                "hp" : pet.hp,
                "happiness" : pet.happiness,
                "hunger" : pet.hunger,
                "hunger_penalty_count" : pet.hunger_penalty_count,
                "is_alive" : pet.is_alive
            }

        return {
            "name" : "",
            "hp" : 0,
            "happiness" : 0,
            "hunger" : 0,
            "hunger_penalty_count" : 0,
            "is_alive" : pet.is_alive
        }

    def pet_pull(self) -> None:
        # получает строку из бд в формате
        # id name hp happiness hunger hunger_penalty_count is_alive
        # и передает их как переменные
        self.__pets[id] = Pet(hp, happiness, hunger, hunger_penalty_count, is_alive)

    def pet_push(self, id : int) -> None:
        pet = {"id" : id} | self.__stat(id)
        # отправляешь питомца в бд

pet_service = PetService()
