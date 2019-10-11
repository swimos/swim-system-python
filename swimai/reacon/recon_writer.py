from abc import ABC, abstractmethod

from swimai.structure.attr import Attr
from swimai.structure.field import Field
from swimai.structure.record import Record
from swimai.structure.slot import Slot
from swimai.structure.value import Value


class ReconWriter(ABC):

    async def write_attr(self, key, value):
        pass

    async def write_slot(self, key, value):
        pass

    @abstractmethod
    async def write_value(self, value):
        ...


class ReconStructureWriter(ReconWriter):

    async def write_item(self, item):

        if isinstance(item, Field):
            if isinstance(item, Attr):
                return await self.write_attr(item.key, item.value)
            elif isinstance(item, Slot):
                return await self.write_slot(item.key, item.value)
        elif isinstance(item, Value):
            return await self.write_value(item)

        # TODO add exception
        return f'No Recon serialization for {item}'

    async def write_value(self, value):
        if isinstance(value, Record):
            # return self.write_record(value)
            pass
        # elif isinstance(value, Data):
        #     return self.write_data(value)
        # elif isinstance(value, Text):
        #     return self.write_text(value)
