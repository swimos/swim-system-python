from typing import Optional


class ReconUtils:

    @staticmethod
    async def is_ident_start_char(char: (str, int)) -> bool:
        """
        Check if a character is a valid first character of an identifier.
        Valid start characters for identifiers: [A-Za-z_]

        :param char:        - Character to check.
        :return:            - True if the character is valid, False otherwise.
        """
        if char:
            char = await ReconUtils.to_ord(char)

            return ord('A') <= char <= ord('Z') or char == ord('_') or ord('a') <= char <= ord('z')
        else:
            return False

    @staticmethod
    async def is_ident_char(char: (str, int)) -> bool:
        """
        Check if a character is a valid character of an identifier.
        Valid characters for identifiers: [A-Za-z_-]

        :param char:        - Character to check.
        :return:            - True if the character is valid, False otherwise.
        """
        if char:
            char = await ReconUtils.to_ord(char)
            return char == ord('-') or await ReconUtils.is_digit(char) or await ReconUtils.is_ident_start_char(char)
        else:
            return False

    @staticmethod
    async def is_space(char: (str, int)) -> bool:
        """
        Check if a character is a space character.

        :param char:        - Character to check.
        :return:            - True if the character is a space character, False otherwise.
        """
        if char:
            char = await ReconUtils.to_ord(char)
            return char == ord(' ') or char == ord('\t')
        else:
            return False

    @staticmethod
    async def is_digit(char: (str, int)) -> bool:
        """
       Check if a character is a digit.

       :param char:         - Character to check.
       :return:             - True if the character is a digit, False otherwise.
       """
        if char:
            char = await ReconUtils.to_ord(char)
            return ord('0') <= char <= ord('9')
        else:
            return False

    @staticmethod
    async def to_ord(char: (str, int)) -> Optional[int]:
        """
        Convert a character to its integer representation.

        :param char:        - Character to convert.
        :return:            - Integer representation of the character.
        """
        if isinstance(char, str):
            return ord(char)
        if isinstance(char, int):
            return char
        else:
            return None
