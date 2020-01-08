#  Copyright 2015-2020 SWIM.AI inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from swimai.structures.structs import Value
from .parsers import ReconParser
from .writers import ReconWriter


class Recon:
    # Singletons
    writer = None
    parser = None

    @staticmethod
    async def parse(recon_string: str) -> 'Value':
        """
        Parse a Recon message in string format and return a Swim structure object.

        :param recon_string:        - Recon message in string format.
        :return:                    - Swim structure object representing the Recon message.
        """
        return await Recon.get_parser().parse_block_string(recon_string)

    @staticmethod
    async def to_string(item: 'Value') -> str:
        """
        Parse a Swim structure object to a Recon string.

        :param item:               - Swim structure object.
        :return:                   - Recon message in string format representing the Swim structure object.
        """
        return await Recon.get_writer().write_item(item)

    @staticmethod
    def get_writer() -> 'ReconWriter':
        """
        Get a Recon writer if one already exists.
        Otherwise, instantiate a new one.

        :return:        - Recon writer.
        """
        if Recon.writer is None:
            Recon.writer = ReconWriter()

        return Recon.writer

    @staticmethod
    def get_parser() -> 'ReconParser':
        """
        Get a Recon parser if one already exists.
        Otherwise, instantiate a new one.

        :return:        - Recon parser.
        """
        if Recon.parser is None:
            Recon.parser = ReconParser()

        return Recon.parser
