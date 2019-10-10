class Value:

    @staticmethod
    def absent():
        return Absent.absent()

    def to_value(self):
        return self

    def length(self):
        return 0


class Absent(Value):
    # TODO: Convert to singleton
    def __init__(self):
        pass

    @staticmethod
    def absent():
        return Absent()
