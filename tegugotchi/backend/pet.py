class Pet:
    def __init__(self, name: str, hp: int) -> None:
        if hp <= 0:
            raise ValueError("Возраст не может быть отрицательным или нулевым!")
        self.__name : str = name
        self.__hp : int = hp
        self.__happyness : int = 2
        self.__hunger : int = 2

        self.__hgCounter : int = 0
        self.__isAlive : bool = True

    def __ensure_alive(self) -> None:
        if not self.__isAlive:
            raise ValueError("Питомец неактивен")

    def disappeared(self) -> None:
        self.__ensure_alive()
        self.__isAlive = False
        print("Питомец ушёл")

    def change_hp(self, value : int) -> None:
        if not self.is_alive:
            return
        self.__hp += value
        if self.__hp <= 0:
            self.disappeared()

    def change_happyness(self, value : int) -> None:
        if not self.is_alive:
            return
        self.__happyness += value
        if self.__happyness <= 0:
            self.disappeared()

    def change_hunger(self, value : int) -> None:
        if not self.is_alive:
            return
        self.__hunger += value
        self.__hunger = max(0, self.__hunger)

        if self.__hunger > 5:
            self.change_hp(-(1 + self.__hgCounter))
            self.__hgCounter += 1
        else:
            self.__hgCounter = 0

    def feed(self) -> None:
        self.__ensure_alive()
        self.change_hunger(-2)

    def pat(self) -> None:
        self.__ensure_alive()
        self.change_happyness(+1)
        self.change_hunger(+1)

    def delicious_feed(self) -> None:
        self.__ensure_alive()
        self.change_happyness(+2)
        self.change_hunger(-1)

    def walk(self) -> None:
        self.__ensure_alive()
        self.change_happyness(+1)
        self.change_hunger(+3)

    def ignore(self) -> None:
        self.__ensure_alive()
        self.change_happyness(-1)
        self.change_hunger(+1)

    @property
    def hp(self) -> int:
        self.__ensure_alive()
        return self.__hp

    @property
    def name(self) -> str:
        self.__ensure_alive()
        return self.__name

    @property
    def happyness(self) -> int:
        self.__ensure_alive()
        return self.__happyness

    @property
    def hunger(self) -> int:
        self.__ensure_alive()
        return self.__hunger

    @property
    def is_alive(self) -> bool:
        return self.__isAlive
