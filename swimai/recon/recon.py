from swimai.structures.structs import Value
from swimai.recon.parsers import ReconStructureParser
from swimai.recon.writers import ReconStructureWriter


class Recon:
    # Singletons
    structure_writer = None
    structure_parser = None

    @staticmethod
    async def parse(recon_string: str) -> 'Value':
        """
        Parse a Recon message in string format and return a Swim structure object.

        :param recon_string:        - Recon message in string format.
        :return:                    - Swim structure object representing the Recon message.
        """
        return await Recon.get_structure_parser().parse_block_string(recon_string)

    @staticmethod
    async def to_string(item):
        """
        Parse a Swim structure object to a Recon string.

        :param item:               - Swim structure object.
        :return:                   - Recon message in string format representing the Swim structure object.
        """
        return await Recon.get_structure_writer().write_item(item)

    @staticmethod
    def get_structure_writer():
        """
        Get a Recon writer if one already exists.
        Otherwise, instantiate a new one.

        :return:        - Recon writer.
        """
        if Recon.structure_writer is None:
            Recon.structure_writer = ReconStructureWriter()

        return Recon.structure_writer

    @staticmethod
    def get_structure_parser():
        """
        Get a Recon parser if one already exists.
        Otherwise, instantiate a new one.

        :return:        - Recon parser.
        """
        if Recon.structure_parser is None:
            Recon.structure_parser = ReconStructureParser()

        return Recon.structure_parser
