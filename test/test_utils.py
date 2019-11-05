from swimai import Item


class CustomString:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        return f'CustomString({self.value})'


class CustomItem(Item):
    @property
    def key(self) -> 'Any':
        return 'MockKey'

    @property
    def value(self) -> 'Any':
        return 'MockVale'
