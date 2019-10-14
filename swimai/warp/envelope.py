from abc import ABC, abstractmethod

from swimai.reacon.writers import Recon


class Envelope(ABC):

    async def to_recon(self):
        """
        Create a Recon message from Envelope.
        :return:
        """
        return await Recon.to_string(self.to_value())

    def to_value(self):
        """
        Create a value object from Envelope.
        :return:
        """
        return self.get_form().mold(self).to_value()

    @abstractmethod
    def get_form(self):
        ...

    @abstractmethod
    def tag(self):
        ...

    @staticmethod
    def parse_recon(recon_message):
        """
        Parses a Recon message into an Envelope object.
        :return:
        """
        value = Recon.parse(recon_message)
        return Envelope.create_from_value(value)

    @staticmethod
    def create_from_value(value):
        """
        Create an Envelope from a Value object.
        :param value:
        :return:
        """

        pass
