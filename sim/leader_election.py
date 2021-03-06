class LeaderElection:
    def __init__(self, node, network):
        self.node = node
        self.network = network

    def get_leader(self):
        raise NotImplementedError  # pragma: no cover


class RoundRobinLE(LeaderElection):
    def get_leader(self, round=None):
        nodes = list(self.network.nodes.values())
        nodes.sort(key=lambda n: n.name)
        round = self.node.round if round is None else round
        print([nodes[round % len(nodes)].name])
        return [nodes[round % len(nodes)].name]
