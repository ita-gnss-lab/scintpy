def foo() -> None:
    number = input("What is your favourite number? ")
    print("It is", number + "1")  # mypy test
    print("bar!")
