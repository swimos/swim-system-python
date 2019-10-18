class ReconUtils:

    @staticmethod
    async def is_ident_start_char(c):
        if c:
            c = ord(c)
            return ord('A') <= c <= ord('Z') or c == ord('_') or ord('a') <= c <= ord(
                'z') or 0xc0 <= c <= 0xd6 or 0xd8 <= c <= 0xf6 or 0xf8 <= c <= 0x2ff or 0x370 <= c <= 0x37d or 0x37f <= c <= 0x1fff or 0x200c <= c <= 0x200d or 0x2070 <= c <= 0x218f or 0x2c00 <= c <= 0x2fef or 0x3001 <= c <= 0xd7ff or 0xf900 <= c <= 0xfdcf or 0xfdf0 <= c <= 0xfffd or 0x10000 <= c <= 0xeffff
        else:
            return False

    @staticmethod
    async def is_ident_char(c):
        if c:
            c = ord(c)
            return c == ord('-') or ord('0') <= c <= ord('9') or ord('A') <= c <= ord('Z') or c == ord('_') or ord('a') <= c <= ord(
                'z') or c == 0xb7 or 0xc0 <= c <= 0xd6 or 0xd8 <= c <= 0xf6 or 0xf8 <= c <= 0x37d or 0x37f <= c <= 0x1fff or 0x200c <= c <= 0x200d or 0x203f <= c <= 0x2040 or 0x2070 <= c <= 0x218f or 0x2c00 <= c <= 0x2fef or 0x3001 <= c <= 0xd7ff or 0xf900 <= c <= 0xfdcf or 0xfdf0 <= c <= 0xfffd or 0x10000 <= c <= 0xeffff
        else:
            return False

    @staticmethod
    async def is_space(c):
        if c:
            c = ord(c)
            return c == ord(' ') or c == ord('\t')
        else:
            return False

    @staticmethod
    async def is_digit(c):
        if c:
            c = ord(c)
            return ord('0') <= c <= ord('9')
        else:
            return False
