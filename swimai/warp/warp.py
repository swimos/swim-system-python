import math
from abc import ABC, abstractmethod
from typing import Optional

from swimai.recon.recon import Recon
from swimai.structures.structs import Item, Record, Attr, Value, Num, RecordMap


class Envelope(ABC):

    def __init__(self, node_uri: str, lane_uri: str, tag: str, form: 'Form', body: Item = Value.absent()) -> None:
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.tag = tag
        self.form = form
        self.body = body

    @staticmethod
    async def parse_recon(recon_message: str) -> 'Envelope':
        """
        Parse a Recon message in string format into an Envelope.

        :param recon_message    - Recon message in string format.
        :return:                - Envelope from the Recon message.
        """
        value = await Recon.parse(recon_message)
        return Envelope.create_from_value(value)

    @staticmethod
    def create_from_value(value: RecordMap) -> 'Envelope':
        """
        Parse a Swim value object into an Envelope.

        :param value:           - Swim value object.
        :return:                - Envelope from the Swim value object.
        """
        tag = value.tag
        form = Envelope.resolve_form(tag)

        return form.cast(value)

    @staticmethod
    def resolve_form(tag: str) -> 'Form':
        """
        Returns a Swim form corresponding to a given tag.

        :param tag:             - Name of the tag as string.
        :return:                - The form corresponding to the tag.
        """
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

    async def to_recon(self) -> str:
        """
        Create a Recon message in string format representing this Envelope.

        :return:                - Recon message in string format from this Envelope.
        """
        return await Recon.to_string(self.to_value())

    def to_value(self) -> Value:
        """
        Create a Swim value object representing this Envelope.

        :return:                - Swim value object from this Envelope.
        """
        return self.form.mold(self)


class LinkAddressedEnvelope(Envelope):

    def __init__(self, node_uri: str, lane_uri: str, prio: float, rate: float, tag: str, form: 'Form', body: Item = Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, tag, form, body)
        self.prio = prio
        self.rate = rate


class LaneAddressedEnvelope(Envelope):

    def __init__(self, node_uri: str, lane_uri: str, tag: str, form: 'Form', body=Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, tag, form, body)


class SyncRequest(LinkAddressedEnvelope):

    def __init__(self, node_uri: str, lane_uri: str, prio: float = 0.0, rate: float = 0.0, body: Item = Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, prio, rate, tag='sync', form=SyncRequestForm(), body=body)


class LinkedResponse(LinkAddressedEnvelope):

    def __init__(self, node_uri: str, lane_uri: str, prio: float = 0.0, rate: float = 0.0, body: Item = Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, prio, rate, tag='linked', form=LinkedResponseForm(), body=body)


class SyncedResponse(LaneAddressedEnvelope):

    def __init__(self, node_uri: str, lane_uri: str, body: Item = Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, tag='synced', form=SyncedResponseForm(), body=body)


class CommandMessage(LaneAddressedEnvelope):

    def __init__(self, node_uri: str, lane_uri: str, body: Item = Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, tag='command', form=CommandMessageForm(), body=body)


class EventMessage(LaneAddressedEnvelope):

    def __init__(self, node_uri: str, lane_uri: str, body: Item = Value.absent()) -> None:
        super().__init__(node_uri, lane_uri, tag='event', form=EventMessageForm(), body=body)


class Form(ABC):

    @property
    @abstractmethod
    def tag(self) -> str:
        """
        Return the tag associated with the given Form object.

        :return:                - Name of the tag as string value.
        """
        ...

    @abstractmethod
    def mold(self, envelope: 'Envelope') -> 'Value':
        """
        Create a value object from a given Envelope.

        :param envelope:        - Envelope to convert to Value object.
        :return:                - Value object representing the Envelope.
        """
        ...

    @abstractmethod
    def cast(self, item: RecordMap) -> 'Envelope':
        """
        Create an Envelope object from a RecordMap.

        :param item:            - RecordMap to convert to Envelope.
        :return:                - Envelope object created from the RecordMap.
        """
        ...


class LinkAddressedForm(Form):

    @abstractmethod
    def create_envelope_from(self, node_uri: str, lane_uri: str, prio: float, rate: float, body: 'Item') -> 'Envelope':
        """
        Create an Envelope object corresponding to the given LinkAddressedForm.

        :param node_uri:        - Node URI of the Envelope.
        :param lane_uri:        - Lane URI of the Envelope.
        :param prio:            - Priority of the Envelope.
        :param rate:            - Rate of the Envelope.
        :param body:            - Body of the Envelope.
        :return:                - Envelope corresponding to the LinkAddressedForm.
        """
        ...

    def mold(self, envelope: Optional['LinkAddressedEnvelope']) -> 'Value':

        if envelope is not None:

            headers = Record.create().add_slot('node', envelope.node_uri).add_slot('lane', envelope.lane_uri)
            prio = envelope.prio

            if prio != 0 and not math.isnan(prio):
                headers.add_slot('prio', Num.create_from(prio))

            rate = envelope.rate

            if rate != 0 and not math.isnan(rate):
                headers.add_slot('rate', Num.create_from(rate))

            return Attr.create_attr(self.tag, headers).concat(envelope.body)
        else:
            return Item.extant()

    def cast(self, value: RecordMap) -> Optional['Envelope']:
        headers = value.get_headers(self.tag)
        node_uri = None
        lane_uri = None
        prio = 0.0
        rate = 0.0

        for index in range(0, headers.size):
            header = headers.get_item(index)
            key = header.key.get_string_value()

            if key is not None:

                if key == 'node':
                    node_uri = header.value.get_string_value()
                elif key == 'lane':
                    lane_uri = header.value.get_string_value()
                elif key == 'prio':
                    prio = header.value.get_num_value()
                elif key == 'rate':
                    rate = header.value.get_num_value()

        if node_uri is not None and lane_uri is not None:
            body = value.get_body()
            return self.create_envelope_from(node_uri, lane_uri, prio, rate, body)


class LaneAddressedForm(Form):

    @abstractmethod
    def create_envelope_from(self, node_uri, lane_uri, body) -> 'Envelope':
        """
        :param node_uri:        - Node URI of the Envelope.
        :param lane_uri:        - Lane URI of the Envelope.
        :param body:            - Body of the Envelope.
        :return:                - Envelope corresponding to the LaneAddressedForm.
        """
        ...

    def mold(self, envelope: Optional['LaneAddressedEnvelope']) -> 'Value':

        if envelope is not None:
            headers = Record.create().add_slot('node', envelope.node_uri).add_slot('lane', envelope.lane_uri)
            return Attr.create_attr(self.tag, headers).concat(envelope.body)
        else:
            return Item.extant()

    def cast(self, item: 'RecordMap') -> Optional['Envelope']:
        value = item
        headers = value.get_headers(self.tag)
        node_uri = None
        lane_uri = None

        for index in range(0, headers.size):
            header = headers.get_item(index)
            key = header.key.get_string_value()

            if key is not None:

                if key == 'node':
                    node_uri = header.value.get_string_value()
                elif key == 'lane':
                    lane_uri = header.value.get_string_value()

        if node_uri is not None and lane_uri is not None:
            body = value.get_body()
            return self.create_envelope_from(node_uri, lane_uri, body)


class SyncedResponseForm(LaneAddressedForm):

    @property
    def tag(self) -> str:
        return 'synced'

    def create_envelope_from(self, node_uri, lane_uri, body) -> 'Envelope':
        return SyncedResponse(node_uri, lane_uri, body=body)


class SyncRequestForm(LinkAddressedForm):

    @property
    def tag(self) -> str:
        return 'sync'

    def create_envelope_from(self, node_uri, lane_uri, prio, rate, body) -> 'Envelope':
        return SyncRequest(node_uri, lane_uri, prio, rate, body=body)


class LinkedResponseForm(LinkAddressedForm):

    @property
    def tag(self) -> str:
        return 'linked'

    def create_envelope_from(self, node_uri, lane_uri, prio, rate, body) -> 'Envelope':
        return LinkedResponse(node_uri, lane_uri, prio, rate, body=body)


class CommandMessageForm(LaneAddressedForm):

    @property
    def tag(self) -> str:
        return 'command'

    def create_envelope_from(self, node_uri, lane_uri, body) -> 'Envelope':
        return CommandMessage(node_uri, lane_uri, body=body)


class EventMessageForm(LaneAddressedForm):

    @property
    def tag(self) -> str:
        return 'event'

    def create_envelope_from(self, node_uri, lane_uri, body) -> 'Envelope':
        return EventMessage(node_uri, lane_uri, body)
