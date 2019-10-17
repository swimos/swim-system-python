from abc import ABC, abstractmethod

from swimai.reacon.reacon import Recon
from swimai.warp.forms import SyncedResponseForm


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

    @staticmethod
    async def parse_recon(recon_message):
        """
        Parses a Recon message into an Envelope object.
        :return:
        """
        value = await Recon.parse(recon_message)
        return Envelope.create_from_value(value)

    @staticmethod
    def create_from_value(value):
        """
        Create an Envelope from a Value object.
        :param value:
        :return:
        """
        tag = value.tag
        form = Envelope.resolve_form(tag)

        if form is not None:
            return form.cast(value)
        else:
            return None

    @staticmethod
    def resolve_form(tag):
        if tag == 'synced':
            return SyncedResponseForm()

    @abstractmethod
    def get_form(self):
        ...

    @abstractmethod
    def tag(self):
        ...
