from swimai.structure.structs import Value
from swimai.warp.envelope import Envelope
from swimai.warp.forms import LinkAddressedForm


class SyncRequest(Envelope):

    def __init__(self, node_uri, lane_uri, prio=0.0, rate=0.0, body=Value.absent()):
        self.node_uri = node_uri
        self.lane_uri = lane_uri
        self.prio = prio
        self.rate = rate
        self.body = body
        self.form = SyncRequestForm()

    @property
    def tag(self):
        return "sync"

    def get_form(self):
        return self.form


class SyncRequestForm(LinkAddressedForm):

    @property
    def tag(self):
        return "sync"
