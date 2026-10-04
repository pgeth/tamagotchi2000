class Pet:
    def __init__(self, name: str, hp: int) -> None:
        if hp <= 0:
            raise ValueError("Возраст не может быть отрицательным или нулевым!")
        self.__name : str = name
        self.__hp : int = hp
        self.__happyness : int = 2
        self.__hunger : int = 2

        self.__hgCounter : int = 0

    def disappeared(self) -> None:
        ...

    def change_hp(self, value : int) -> None:
        self.__hp += value
        if self.__hp <= 0:
            self.disappeared()

    def change_happyness(self, value : int) -> None:
        self.__happyness += value
        if self.__happyness <= 0:
            self.disappeared()

    def change_hunger(self, value : int) -> None:
        self.__hunger += value
        self.__hunger = max(0, self.__hunger)

        if self.__hunger >= 5:
            self.change_hp(-(1 + self.__hgCounter))
            self.__hgCounter += 1
        else:
            self.__hgCounter = 0

    def feed(self) -> None:
        self.change_hunger(-2)

    def pat(self) -> None:
        self.change_happyness(+1)
        self.change_hunger(+1)

    def delicious_feed(self) -> None:
        self.change_happyness(+2)
        self.change_hunger(-1)

    def walk(self) -> None:
        self.change_happyness(+1)
        self.change_hunger(+3)

    def ignore(self) -> None:
        self.change_happyness(-1)
        self.change_hunger(+1)

    @property
    def hp(self) -> int:
        return self.__hp

    @property
    def name(self) -> str:
        return self.__name

    @property
    def happyness(self) -> int:
        return self.__happyness

    @property
    def hunger(self) -> int:
        return self.__hunger
