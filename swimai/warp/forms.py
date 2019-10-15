import math
from abc import ABC, abstractmethod

from swimai.structure.structs import Item, Record, Attr


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
