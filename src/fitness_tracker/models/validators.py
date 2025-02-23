def is_positive_number(number: float) -> float:
    if number > 0:
        return number

    raise ValueError


def is_non_negative(number: float) -> float:
    if number >= 0:
        return number

    raise ValueError
