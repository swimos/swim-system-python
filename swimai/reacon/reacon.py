from swimai.reacon.parsers import ReconStructureParser
from swimai.reacon.writers import ReconStructureWriter


class Recon:
    structure_writer = None
    structure_parser = None

    @staticmethod
    async def parse(recon_string):
        """
        Parse a string and return a Value object.
        :param recon_string:
        :return:
        """
        return await Recon.get_structure_parser().parse_block_string(recon_string)

    @staticmethod
    async def to_string(item):
        """
        Parse an Item object to string.
        :return:
        """
        return await Recon.write(item)

    @staticmethod
    async def write(item):
        return await Recon.get_structure_writer().write_item(item)

    @staticmethod
    def get_structure_writer():
        if Recon.structure_writer is None:
            Recon.structure_writer = ReconStructureWriter()

        return Recon.structure_writer

    @staticmethod
    def get_structure_parser():
        if Recon.structure_parser is None:
            Recon.structure_parser = ReconStructureParser()

        return Recon.structure_parser
