from swimai.structure.structs import Value
from swimai.warp.envelope import Envelope
from swimai.warp.forms import CommandMessageForm


class CommandMessage(Envelope):

    def __init__(self, node_uri, lane_uri, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.body = body
        self.form = CommandMessageForm()

    @property
    def tag(self):
        return "command"

    def get_form(self):
        return self.form
