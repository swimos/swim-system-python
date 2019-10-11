class Value:

    @staticmethod
    def absent():
        return Absent.get_absent()

    def to_value(self):
        return self

    def length(self):
        return 0


class Text(Value):
    empty = None

    def __init__(self, value):
        self.value = value

    @staticmethod
    def get_from(string):
        if not string:
            return Text.get_empty()
        return Text(string)

    @staticmethod
    def get_empty():
        if Text.empty is None:
            Text.empty = Text('')

        return Text.empty


class Absent(Value):
    absent = None

    def __init__(self):
        pass

    @staticmethod
    def get_absent():
        if Absent.absent is None:
            Absent.absent = Absent()

        return Absent
