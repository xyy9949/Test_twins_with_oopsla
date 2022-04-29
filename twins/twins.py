from sim.network import Network
from sim.leader_election import LeaderElection


class TwinsNetwork(Network):
    def __init__(self, env, model, firewall, num_of_twins, num_of_rounds):
        super().__init__(env, model)
        self.firewall = firewall
        self.num_of_twins = num_of_twins
        self.num_of_rounds = num_of_rounds

    @property
    def quorum(self):
        sole_nodes = len(self.nodes) - self.num_of_twins
        f = (sole_nodes - 1) // 3
        return sole_nodes - f - 2

    def send(self, fromx, tox, message):
        if fromx.round <= self.num_of_rounds:
            self.env.process(self._send(fromx, tox, message))


class TwinsLE(LeaderElection):
    def __init__(self, node, network, round_leaders):
        super().__init__(node, network)
        self.round_leaders = round_leaders

    def get_leader(self, round=None):
        round = self.node.round if round is None else round
        if str(round) in self.round_leaders:
            return self.round_leaders[str(round)]
        else:
            return []
