class Pet:
    def __init__(self, name: str, hp: int) -> None:
        if hp <= 0:
            raise ValueError("Здоровье должно быть больше нуля")
        self.__name : str = name
        self.__hp : int = hp
        self.__happiness : int = 2
        self.__hunger : int = 2

        self.__hunger_penalty_count : int = 0
        self.__is_alive : bool = True

    def __ensure_alive(self) -> None:
        if not self.__is_alive:
            raise ValueError("Питомец неактивен")

    def disappeared(self) -> None:
        self.__ensure_alive()
        self.__is_alive = False

    def __change_hp(self, value : int) -> None:
        if not self.is_alive:
            return
        self.__hp += value
        if self.__hp <= 0:
            self.disappeared()

    def __change_happiness(self, value : int) -> None:
        if not self.is_alive:
            return
        self.__happiness += value
        if self.__happiness <= 0:
            self.disappeared()

    def __change_hunger(self, value : int) -> None:
        if not self.is_alive:
            return
        self.__hunger += value
        self.__hunger = max(0, self.__hunger)

        if self.__hunger >= 5:
            self.__change_hp(-(1 + self.__hunger_penalty_count))
            self.__hunger_penalty_count += 1
        else:
            self.__hunger_penalty_count = 0

    def feed(self) -> None:
        self.__ensure_alive()
        self.__change_hunger(-2)

    def pat(self) -> None:
        self.__ensure_alive()
        self.__change_happiness(+1)
        self.__change_hunger(+1)

    def treat(self) -> None:
        self.__ensure_alive()
        self.__change_happiness(+2)
        self.__change_hunger(-1)

    def walk(self) -> None:
        self.__ensure_alive()
        self.__change_happiness(+1)
        self.__change_hunger(+3)

    def ignore(self) -> None:
        self.__ensure_alive()
        self.__change_happiness(-1)
        self.__change_hunger(+1)

    @property
    def hp(self) -> int:
        self.__ensure_alive()
        return self.__hp

    @property
    def name(self) -> str:
        self.__ensure_alive()
        return self.__name

    @property
    def happiness(self) -> int:
        self.__ensure_alive()
        return self.__happiness

    @property
    def hunger(self) -> int:
        self.__ensure_alive()
        return self.__hunger

    @property
    def is_alive(self) -> bool:
        return self.__is_alive
