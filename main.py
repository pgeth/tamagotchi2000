from tegugotchi.backend.pet import Pet

def main() -> None:
    Grog = Pet("Grog", 40)
    Grog.change_hp(50)
    print(Grog)

if __name__ == "__main__":
   main()
