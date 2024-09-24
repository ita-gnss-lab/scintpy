def foo() -> None:
    number = input("What is your favourite number? ")
    print("It is", number + "1!")  # mypy test
    x = "{} {}".format(1, 2)  # pyupgrade
    print(x)
