from swimai.reacon.writers import ReconStructureWriter


class Recon:
    structure_writer = None

    @staticmethod
    def parse(string):
        """
        Parse a string and return Value object.
        :param string:
        :return:
        """
        pass

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
