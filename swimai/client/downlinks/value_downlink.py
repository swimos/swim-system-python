class ValueDownlink:

    def __init__(self, client):
        self.__client = client
        self.host_uri = None
        self.node_uri = None
        self.lane_uri = None

    def set_host_uri(self, host_uri):
        self.host_uri = host_uri
        return self

    def set_node_uri(self, node_uri):
        self.node_uri = node_uri
        return self

    def set_lane_uri(self, lane_uri):
        self.lane_uri = lane_uri
        return self

    def did_set(self, function):
        pass
        return self

    def open(self):
        pass
        return self

    def get(self):
        pass
