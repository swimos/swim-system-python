from abc import ABC

from swimai.structure.record import Record


class LinkedAddressedForm(ABC):

    def mold(self, envelope):

        if envelope is not None:

            headers = Record.create(4)

    def cast(self):
        pass
