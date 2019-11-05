class WSConnection:

    def __init__(self, websocket):
        self.websocket = websocket
        self.subscribers = 1

    def subscribe(self):
        self.subscribers += 1

    def unsubscribe(self):
        self.subscribers -= 1
