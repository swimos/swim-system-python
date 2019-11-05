from abc import ABC

from swimai.recon.utils import ReconUtils
from swimai.structures.structs import ValueBuilder, Text, Bool, Attr, Value, Record, Slot, Num


class Parser(ABC):
    pass


class BlockParser(Parser):

    @staticmethod
    async def parse(message, parser, key_output=None, value_output=None, builder=None):

        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if builder is None:
            builder = await parser.create_value_builder()

        if key_output is None:
            key_output = await parser.parse_block_expression(message)

        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if message.is_cont():

            if char == ':':
                char = message.step()

            while await ReconUtils.is_space(char):
                char = message.step()

            if value_output is None:
                value_output = await parser.parse_block_expression(message)

            builder.add(await parser.create_slot(key_output, value_output))

            char = message.head()
            if char == ',' or char == ';':
                message.step()
                await BlockParser.parse(message, parser, builder=builder)

            return builder.bind()

        else:
            builder.add(key_output)
            return builder.bind()

    @staticmethod
    async def parse_block(message, parser):
        return await BlockParser.parse(message, parser)


class ReconParser:

    async def parse_attr(self, message):
        return await AttrParser.parse_attr(message, self)

    async def parse_ident(self, message):
        return await IdentParser.parse_ident(message, self)

    async def parse_string(self, message):
        return await StringParser.parse_string(message, self)

    async def parse_number(self, message):
        return await NumberParser.parse_number(message, self)

    async def parse_block_string(self, recon_string):
        message = InputMessage(recon_string)
        return await self.parse_block(message)

    async def parse_block(self, message):
        return await BlockParser.parse_block(message, self)

    async def parse_block_expression(self, message):
        return await self.parse_lambda_func(message)

    async def parse_record(self, message, builder):
        return await RecordParser.parse_record(message, self, builder=builder)

    async def parse_lambda_func(self, message):
        return await LambdaFuncParser.parse_lambda_func(message, self)

    async def parse_conditional_operator(self, message, builder):
        return await ConditionalOperatorParser.parse_conditional_operator(message, self, builder)

    async def parse_or_operator(self, message, builder):
        return await OrOperatorParser.parse_or_operator(message, self, builder)

    async def parse_and_operator(self, message, builder):
        return await AndOperatorParser.parse_and_operator(message, self, builder)

    async def parse_bitwise_or_operator(self, message, builder):
        return await BitwiseOrOperatorParser.parse_bitwise_or_operator(message, self, builder)

    async def parse_bitwise_xor_operator(self, message, builder):
        return await BitwiseXorOperatorParser.parse_bitwise_xor_operator(message, self, builder)

    async def parse_bitwise_and_operator(self, message, builder):
        return await BitwiseAndOperator.parse_bitwise_and_operator(message, self, builder)

    async def parse_comparison_operator(self, message, builder):
        return await ComparisonOperatorParser.parse_comparison_operator(message, self, builder)

    async def parse_attr_expression(self, message, builder):
        return await AttrExpressionParser.parse_attr_expression(message, self, builder)

    async def parse_additive_operator(self, message, builder):
        return await AdditiveOperatorParser.parse_additive_operator(message, self, builder)

    async def parse_multiplicative_operator(self, message, builder):
        return await MultiplicativeOperatorParser.parse_multiplicative_operator(message, self, builder)

    async def parse_prefix_operator(self, message, builder):
        return await PrefixOperatorParser.parse_prefix_operator(message, self, builder)

    async def parse_invoke_operator(self, message, builder):
        return await InvokeOperatorParser.parse_invoke_operator(message, self, builder)

    async def parse_primary(self, message, builder):
        return await PrimaryParser.parse_primary(message, self, builder)

    async def parse_literal(self, message, builder):
        return await LiteralParser.parse_literal(message, self, builder)


class ReconStructureParser(ReconParser):

    async def create_ident(self, value):
        if isinstance(value, str):
            if value == 'true':
                return Bool.create_from(True)
            elif value == 'false':
                return Bool.create_from(False)

        return Text.create_from(value)

    async def create_attr(self, key, value=Value.extant()):
        return Attr.create_attr(key, value)

    async def create_record_builder(self):
        return Record.create()

    async def create_value_builder(self):
        return ValueBuilder()

    async def create_slot(self, key, value=None):
        return Slot.create_slot(key, value)

    async def create_number(self, value):
        return Num.create_from(value)


class RecordParser(Parser):

    @staticmethod
    async def parse_record(message, parser, builder=None):
        return await RecordParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, key_output=None, value_output=None, builder=None):
        char = message.head()

        if char == '{':
            char = message.step()

        while await ReconUtils.is_space(char):
            char = message.step()

        if key_output is None:
            key_output = await parser.parse_block_expression(message)

        while await ReconUtils.is_space(char):
            char = message.step()

        if message.is_cont():
            if message.head() == ':':
                message.step()

                if value_output is None:
                    value_output = await parser.parse_block_expression(message)

                builder.add(await parser.create_slot(key_output, value_output))

            else:
                builder.add(key_output)

        if message.is_cont():
            char = message.head()

            if char == ',' or char == ';':
                message.step()
                await RecordParser.parse_record(message, parser, builder)

            elif char == '}':
                message.step()
                return builder


class LambdaFuncParser(Parser):

    @staticmethod
    async def parse_lambda_func(message, parser):
        return await LambdaFuncParser.parse(message, parser)

    @staticmethod
    async def parse(message, parser, output=None, builder=None):
        if output is None:
            output = await parser.parse_conditional_operator(message, builder=builder)

        return output


class ConditionalOperatorParser(Parser):

    @staticmethod
    async def parse_conditional_operator(message, parser, builder):
        return await ConditionalOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, if_output=None, then_output=None, else_output=None, builder=None):
        if if_output is None:
            if_output = await parser.parse_or_operator(message, builder)

        return if_output


class OrOperatorParser(Parser):

    @staticmethod
    async def parse_or_operator(message, parser, builder):
        return await OrOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_and_operator(message, builder)

        return lhs_output


class AndOperatorParser(Parser):

    @staticmethod
    async def parse_and_operator(message, parser, builder):
        return await AndOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_bitwise_or_operator(message, builder)

        return lhs_output


class BitwiseOrOperatorParser(Parser):

    @staticmethod
    async def parse_bitwise_or_operator(message, parser, builder):
        return await BitwiseOrOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_bitwise_xor_operator(message, builder)

        return lhs_output


class BitwiseXorOperatorParser(Parser):

    @staticmethod
    async def parse_bitwise_xor_operator(message, parser, builder):
        return await BitwiseXorOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_bitwise_and_operator(message, builder)

        return lhs_output


class BitwiseAndOperator(Parser):

    @staticmethod
    async def parse_bitwise_and_operator(message, parser, builder):
        return await BitwiseAndOperator.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_comparison_operator(message, builder)

        return lhs_output


class ComparisonOperatorParser(Parser):

    @staticmethod
    async def parse_comparison_operator(message, parser, builder):
        return await ComparisonOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, operator_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_attr_expression(message, builder)

        return lhs_output


class AttrExpressionParser(Parser):

    @staticmethod
    async def parse_attr_expression(message, parser, builder):
        return await AttrExpressionParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, field_output=None, value_output=None, builder=None):

        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if char == '@':
            if field_output is None:
                field_output = await parser.parse_attr(message)

            if builder is None:
                builder = await parser.create_record_builder()

            builder.add(field_output)

            await AttrExpressionParser.parse(message, parser, builder=builder)

            return builder

        elif await ReconUtils.is_ident_start_char(char) or char == '"' or await ReconUtils.is_digit(char) or char == '-':
            if value_output is None:
                value_output = await parser.parse_additive_operator(message, None)

            if builder is None:
                builder = await parser.create_value_builder()

            builder.add(value_output)
            return builder.bind()

        elif char == '{' or char == '[':
            if builder is None:
                builder = await parser.create_record_builder()

            if value_output is None:
                await parser.parse_additive_operator(message, builder)

            if message.is_cont():
                if message.head() == '@':
                    await AttrExpressionParser.parse(message, parser, builder=builder)


class AttrParser(Parser):

    @staticmethod
    async def parse_attr(message, parser):
        return await AttrParser.parse(message, parser)

    @staticmethod
    async def parse(message, parser, key_output=None, value_output=None):

        char = message.head()
        if char == '@':
            char = message.step()

            if char == '"':
                if key_output is None:
                    key_output = await parser.parse_string(message)
            else:

                if key_output is None:
                    key_output = await parser.parse_ident(message)

                if message.head() == '(' and message.is_cont():
                    message.step()
                else:
                    return await parser.create_attr(key_output)

                if message.head() == ')':
                    message.step()
                    return await parser.create_attr(key_output)
                else:
                    if value_output is None:
                        value_output = await parser.parse_block(message)

                if message.head() == ')':
                    message.step()
                    return await parser.create_attr(key_output, value_output)

        return await parser.create_attr(key_output, value_output)


class IdentParser(Parser):

    @staticmethod
    async def parse_ident(message, parser):
        return await IdentParser.parse(message, parser)

    @staticmethod
    async def parse(message, parser, output=None):

        char = message.head()

        if await ReconUtils.is_ident_start_char(char):
            if output is None:
                output = ''

            output = output + char
            char = message.step()

            while await ReconUtils.is_ident_char(char):
                output = output + char
                char = message.step()

        return await parser.create_ident(output)


class StringParser(Parser):

    @staticmethod
    async def parse_string(message, parser):
        return await StringParser.parse(message, parser)

    @staticmethod
    async def parse(message, parser, output=None):
        char = message.head()

        while await ReconUtils.is_space(char):
            char = message.step()

        if char == '"':

            if output is None:
                output = ''

            char = message.step()

            while char != '"' and message.is_cont():
                output = output + char
                char = message.step()

            message.step()

        return Text.create_from(output)


class NumberParser(Parser):

    @staticmethod
    async def parse_number(message, parser):
        return await NumberParser.parse(message, parser)

    @staticmethod
    async def parse(message, parser, value_output=None, sign_output=1):

        char = message.head()

        if char == '-':
            sign_output = -1
            char = message.step()

        if char == '0':
            char = message.step()
        elif '1' <= char <= '9':
            value_output = sign_output * int(char)
            char = message.step()

            while message.is_cont() and await ReconUtils.is_digit(char):
                value_output = 10 * value_output + sign_output * int(char)
                char = message.step()

        if message.is_cont():
            if char == '.':
                return await DecimalParser.parse_decimal(message, parser, value_output, sign_output)
            else:
                return await parser.create_number(value_output)
        else:
            return await parser.create_number(value_output)


class DecimalParser(Parser):

    @staticmethod
    async def parse_decimal(message, parser, value_output=None, sign_output=None):
        builder = ''

        if sign_output < 0 and value_output is None:
            builder += '-0'
        else:
            if value_output is None:
                value_output = 0

            builder += str(value_output)

        return await DecimalParser.parse(message, parser, builder)

    @staticmethod
    async def parse(message, parser, builder):

        char = message.head()

        if char == '.':
            builder += '.'
            message.step()

            if message.is_cont():
                char = message.head()

                if await ReconUtils.is_digit(char):
                    builder += char
                    char = message.step()

                while message.is_cont() and await ReconUtils.is_digit(char):
                    builder += char
                    char = message.step()

                return await parser.create_number(float(builder))


class AdditiveOperatorParser(Parser):

    @staticmethod
    async def parse_additive_operator(message, parser, builder):
        return await AdditiveOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, operator_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_multiplicative_operator(message, builder)

            char = message.head()

            if char == '+':
                pass
            else:
                return lhs_output


class MultiplicativeOperatorParser(Parser):

    @staticmethod
    async def parse_multiplicative_operator(message, parser, builder):
        return await MultiplicativeOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, lhs_output=None, operator_output=None, rhs_output=None, builder=None):
        if lhs_output is None:
            lhs_output = await parser.parse_prefix_operator(message, builder)

            char = message.head()

            if char == '*':
                pass
            elif char == '/':
                pass
            elif char == '%':
                pass
            else:
                return lhs_output


class PrefixOperatorParser(Parser):

    @staticmethod
    async def parse_prefix_operator(message, parser, builder):
        return await PrefixOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, operator_output=None, rhs_output=None, builder=None):

        char = message.head()

        if char == '!':
            pass
        elif char == '~':
            pass
        elif char == '+':
            pass
        else:
            return await parser.parse_invoke_operator(message, builder)


class InvokeOperatorParser(Parser):

    @staticmethod
    async def parse_invoke_operator(message, parser, builder):
        return await InvokeOperatorParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, expr_output=None, args_output=None, builder=None):
        if expr_output is None:
            expr_output = await parser.parse_primary(message, builder)

            char = message.head()

            if char == '(':
                pass
            else:
                return expr_output


class PrimaryParser(Parser):

    @staticmethod
    async def parse_primary(message, parser, builder):
        return await PrimaryParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, expr_output=None, builder=None):

        char = message.head()

        if char == '(':
            pass
        else:
            if expr_output is None:
                expr_output = await parser.parse_literal(message, builder)

            return expr_output


class LiteralParser(Parser):

    @staticmethod
    async def parse_literal(message, parser, builder):
        return await LiteralParser.parse(message, parser, builder=builder)

    @staticmethod
    async def parse(message, parser, value_output=None, builder=None):
        char = message.head()

        if char == '(':
            pass
        elif char == '{':
            if builder is None:
                builder = await parser.create_record_builder()

            await parser.parse_record(message, builder)

        elif char == '[':
            pass
        elif await ReconUtils.is_ident_start_char(char):
            value_output = await parser.parse_ident(message)
        elif char == '"':
            value_output = await parser.parse_string(message)
        elif char == '-' or await ReconUtils.is_digit(char):
            value_output = await parser.parse_number(message)
        if builder is None:
            builder = await parser.create_value_builder()

        if value_output is not None:
            builder.add(value_output)

        return builder.bind()


class InputMessage:

    def __init__(self, message):
        self.message = message
        self.index = 0

    def head(self):

        if self.is_cont():
            return self.message[self.index]
        else:
            return ''

    def step(self):
        self.index = self.index + 1
        return self.head()

    def is_cont(self):
        if self.index >= len(self.message):
            return False
        else:
            return True
