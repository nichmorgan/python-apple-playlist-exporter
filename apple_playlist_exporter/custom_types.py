from typing import Sequence


class Duration(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, int):
            v = cls.__mili_seconds_to_duration(v)
        elif isinstance(v, str) and v.isnumeric():
            v = cls.__mili_seconds_to_duration(int(v))
        else:
            raise ValueError("Value must be an int or a numeric string")

        return cls(v)

    @staticmethod
    def __mili_seconds_to_duration(value: int) -> str:
        millis = int(value)
        seconds = (millis / 1000) % 60
        seconds = int(seconds)
        minutes = (millis / (1000 * 60)) % 60
        minutes = int(minutes)

        return f"{minutes:02}:{seconds:02}"


class StrList(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Sequence):
            v = ",".join(map(str, v))
        else:
            raise ValueError("Value must be a sequence")

        return cls(v)
