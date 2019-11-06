from typing import Optional, Union


class ReconUtils:

    @staticmethod
    async def is_ident_start_char(char: Union[str, int]) -> bool:
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
    async def is_ident_char(char: Union[str, int]) -> bool:
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
    async def is_ident(value: str) -> bool:
        """
        Check if a string value is a valid identifier.

        :param value:      - Value to check.
        :return:           - True if the value is valid identifier, False otherwise.
        """
        if len(value) == 0:
            return False

        if not await ReconUtils.is_ident_start_char(value[0]):
            return False

        for char in value:
            if not await ReconUtils.is_ident_char(char):
                return False

        return True

    @staticmethod
    async def is_space(char: Union[str, int]) -> bool:
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
    async def is_digit(char: Union[str, int]) -> bool:
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
    async def to_ord(char: Union[str, int]) -> Optional[int]:
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


class OutputMessage:

    def __init__(self) -> None:
        self.message = ''

    @staticmethod
    async def create(chars: str = None) -> 'OutputMessage':
        instance = OutputMessage()

        if chars:
            await instance.append(chars)

        return instance

    @property
    def value(self) -> str:
        return self.message

    @property
    def size(self) -> int:
        return len(self.message)

    @property
    def last_char(self) -> str:
        return self.message[-1]

    async def append(self, chars) -> None:

        if isinstance(chars, str):
            self.message = self.message + chars
        elif isinstance(chars, (float, int)):
            self.message = self.message + str(chars)
        elif isinstance(chars, OutputMessage):
            self.message = self.message + chars.value
        else:
            raise TypeError(f'Item of type {type(chars).__name__} cannot be added to the OutputMessage!')


class InputMessage:

    def __init__(self, message: str) -> None:
        self.message = message
        self.index = 0

    def head(self) -> str:

        if self.is_cont():
            return self.message[self.index]
        else:
            return ''

    def step(self) -> str:
        self.index = self.index + 1
        return self.head()

    def is_cont(self) -> bool:
        if self.index >= len(self.message):
            return False
        else:
            return True
