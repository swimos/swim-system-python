class Extant:
    extant = None

    def __init__(self):
        pass

    @staticmethod
    def get_extant():
        if Extant.extant is None:
            Extant.extant = Extant()

        return Extant()
