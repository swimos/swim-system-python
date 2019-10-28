import math
from abc import ABC, abstractmethod

from swim.recon.recon import Recon
from swim.structures.structs import Item, Record, Attr, Value, Num


class Envelope(ABC):

    async def to_recon(self):
        """
        Create a Recon message in string format representing this Envelope.

        :return:                - Recon message in string format from this Envelope.
        """
        return await Recon.to_string(self.to_value())

    def to_value(self):
        """
        Create a Swim structure object representing this Envelope.

        :return:                - Swim structure object from this Envelope.
        """
        return self.get_form().mold(self).to_value()

    @staticmethod
    async def parse_recon(recon_message):
        """
        Parse a Recon message in string format into an Envelope.

        :param recon_message    - Recon message in string format.
        :return:                - Envelope from the Recon message.
        """
        value = await Recon.parse(recon_message)
        return Envelope.create_from_value(value)

    @staticmethod
    def create_from_value(value):
        """
        Parse a Swim structure object into an Envelope.

        :param value:           - Swim structure object.
        :return:                - Envelope from the Swim structure object.
        """
        tag = value.tag
        form = Envelope.resolve_form(tag)

        if form is not None:
            return form.cast(value)
        else:
            return None

    @staticmethod
    def resolve_form(tag):
        if tag == 'sync':
            return SyncRequestForm()
        if tag == 'synced':
            return SyncedResponseForm()
        if tag == 'linked':
            return LinkedResponseForm()
        if tag == 'event':
            return EventMessageForm()
        if tag == 'command':
            return CommandMessageForm()
        else:
            raise TypeError(f'Invalid form tag: {tag}')

    @abstractmethod
    def get_form(self):
        ...

    @property
    @abstractmethod
    def tag(self):
        ...


class SyncRequest(Envelope):

    def __init__(self, node_uri, lane_uri, prio=0.0, rate=0.0, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.prio = prio
        self.rate = rate
        self.body = body
        self.form = SyncRequestForm()

    @property
    def tag(self):
        return 'sync'

    def get_form(self):
        return self.form


class SyncedResponse(Envelope):

    def __init__(self, node_uri, lane_uri, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.body = body
        self.form = SyncedResponseForm()

    @property
    def tag(self):
        return 'synced'

    def get_form(self):
        return self.form


class LinkedResponse(Envelope):

    def __init__(self, node_uri, lane_uri, prio=0.0, rate=0.0, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.prio = prio
        self.rate = rate
        self.body = body
        self.form = LinkedResponseForm()

    @property
    def tag(self):
        return 'linked'

    def get_form(self):
        return self.form


class CommandMessage(Envelope):

    def __init__(self, node_uri, lane_uri, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.body = body
        self.form = CommandMessageForm()

    @property
    def tag(self):
        return 'command'

    def get_form(self):
        return self.form


class EventMessage(Envelope):

    def __init__(self, node_uri, lane_uri, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.body = body
        self.form = EventMessageForm()

    @property
    def tag(self):
        return 'event'

    def get_form(self):
        return self.form


class LinkAddressedForm(ABC):

    def mold(self, envelope):

        if envelope is not None:

            headers = Record.create().slot('node', envelope.node_uri).slot('lane', envelope.lane_uri)
            prio = envelope.prio

            if prio != 0 and not math.isnan(prio):
                headers.slot('prio', Num.create_from(prio))

            rate = envelope.rate

            if rate != 0 and not math.isnan(rate):
                headers.slot('rate', Num.create_from(rate))

            return Attr.of(self.tag, headers).concat(envelope.body)
        else:
            return Item.extant()

    @property
    @abstractmethod
    def tag(self):
        ...

    @abstractmethod
    def create_from(self, node_uri, lane_uri, prio, rate, body):
        ...

    def cast(self, item):
        value = item.to_value()
        headers = value.get_headers(self.tag)
        node_uri = None
        lane_uri = None
        prio = 0.0
        rate = 0.0

        for index in range(0, headers.size):
            header = headers.get_item(index)
            key = header.key.string_value()

            if key is not None:

                if key == 'node':
                    node_uri = header.value.string_value()
                elif key == 'lane':
                    lane_uri = header.value.string_value()
                elif key == 'prio':
                    prio = header.value.num_value()
                elif key == 'rate':
                    rate = header.value.num_value()

        if node_uri is not None and lane_uri is not None:
            body = value.get_body()
            return self.create_from(node_uri, lane_uri, prio, rate, body)


class LaneAddressedForm(ABC):

    def mold(self, envelope):

        if envelope is not None:
            headers = Record.create().slot('node', envelope.node_uri).slot('lane', envelope.lane_uri)
            return Attr.of(self.tag, headers).concat(envelope.body)
        else:
            return Item.extant()

    @property
    @abstractmethod
    def tag(self):
        ...

    @abstractmethod
    def create_from(self, node_uri, lane_uri, body):
        ...

    def cast(self, item):
        value = item.to_value()
        headers = value.get_headers(self.tag)
        node_uri = None
        lane_uri = None

        for index in range(0, headers.size):
            header = headers.get_item(index)
            key = header.key.string_value()

            if key is not None:

                if key == 'node':
                    node_uri = header.value.string_value()
                elif key == 'lane':
                    lane_uri = header.value.string_value()

        if node_uri is not None and lane_uri is not None:
            body = value.get_body()
            return self.create_from(node_uri, lane_uri, body)


class SyncedResponseForm(LaneAddressedForm):

    @property
    def tag(self):
        return 'synced'

    def create_from(self, node_uri, lane_uri, body):
        return SyncedResponse(node_uri, lane_uri, body=body)


class SyncRequestForm(LinkAddressedForm):

    @property
    def tag(self):
        return 'sync'

    def create_from(self, node_uri, lane_uri, prio, rate, body):
        return SyncRequest(node_uri, lane_uri, prio, rate, body=body)


class LinkedResponseForm(LinkAddressedForm):

    @property
    def tag(self):
        return 'linked'

    def create_from(self, node_uri, lane_uri, prio, rate, body):
        return LinkedResponse(node_uri, lane_uri, prio, rate, body=body)


class CommandMessageForm(LaneAddressedForm):

    @property
    def tag(self):
        return 'command'

    def create_from(self, node_uri, lane_uri, body):
        return CommandMessage(node_uri, lane_uri, body=body)


class EventMessageForm(LaneAddressedForm):

    @property
    def tag(self):
        return 'event'

    def create_from(self, node_uri, lane_uri, body):
        return EventMessage(node_uri, lane_uri, body)
