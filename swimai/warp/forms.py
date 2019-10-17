import math
from abc import ABC, abstractmethod

from swimai.structure.structs import Item, Record, Attr, Value, Absent
from swimai.warp.synced_response import SyncedResponse


class LinkAddressedForm(ABC):

    def mold(self, envelope):

        if envelope is not None:

            headers = Record.create().slot("node", envelope.node_uri).slot("lane", envelope.lane_uri)
            prio = envelope.prio

            if prio != 0 and not math.isnan(prio):
                headers.slot('prio', prio)

            rate = envelope.rate

            if rate != 0 and not math.isnan(rate):
                headers.slot('rate', rate)

            return Attr.of(self.tag, headers).concat(envelope.body)
        else:
            return Item.extant()

    @property
    @abstractmethod
    def tag(self):
        ...

    def cast(self, item):
        pass


class LaneAddressedForm(ABC):

    def mold(self, envelope):

        if envelope is not None:
            headers = Record.create().slot("node", envelope.node_uri).slot("lane", envelope.lane_uri)
            return Attr.of(self.tag, headers).concat(envelope.body)
        else:
            return Item.extant()

    @property
    @abstractmethod
    def tag(self):
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
            # body = value.get_body()
            body = Absent.get_absent()
            return self.create_from(node_uri, lane_uri, None)


class SyncedResponseForm(LaneAddressedForm):

    @property
    def tag(self):
        return 'synced'

    # TODO remove circular dependency
    def create_from(self, node_uri, lane_uri, body):
        return SyncedResponse(node_uri, lane_uri, body=body)


class SyncRequestForm(LinkAddressedForm):

    @property
    def tag(self):
        return "sync"


class CommandMessageForm(LaneAddressedForm):

    @property
    def tag(self):
        return "command"
