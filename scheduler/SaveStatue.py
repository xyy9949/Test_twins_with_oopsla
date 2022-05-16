class SaveStatue:
    def __init__(self, num_of_followers, num_of_leaders):
        self.round_statue_dict = dict(dict())
        self.num_of_followers = num_of_followers
        self.num_of_leaders = num_of_leaders

    def can_add_dict(self, round_statue):
        if isinstance(round_statue, RoundStatue):
            if round_statue.current_round % 2 == 0:
                # vote round
                if len(round_statue.node_statue_dict) == self.num_of_followers:
                    return True
            else:
                # leader send bk round
                if len(round_statue.node_statue_dict) == self.num_of_leaders:
                    return True
        return False

    def add_round_statue(self, round_statue):
        if isinstance(round_statue, RoundStatue):
            if self.round_statue_dict.get(round_statue.current_round).get(round_statue.current_phase) is None:
                self.round_statue_dict[round_statue.current_round][round_statue.current_phase] = round_statue

    def check_dict(self, round_statue):
        if isinstance(round_statue, RoundStatue):
            target_round_dict = self.round_statue_dict.get(round_statue.current_round)
            for x in target_round_dict.values():
                if round_statue == x:
                    return True
            return False


class RoundStatue:
    def __init__(self, current_phase, current_round):
        self.current_phase = current_phase
        # >= 3
        self.current_round = current_round
        self.node_statue_dict = dict()

    def add_node_statue(self, dict_key, node_statue):
        if self.node_statue_dict.get(dict_key) is None:
            self.node_statue_dict[dict_key] = node_statue

    def __eq__(self, other):
        if self.node_statue_dict == other.node_statue_dict:
            return True
        else:
            return False


class NodeStatue:
    def __init__(self, statue_round, node_name, highest_qc, highest_qc_round, last_voted_round, preferred_round,
                 committed, votes):
        self.statue_round = statue_round
        self.node_name = node_name
        # digest string
        #  qc.__repr__()
        self.highest_qc = highest_qc
        self.highest_qc_round = highest_qc_round
        self.last_voted_round = last_voted_round
        self.preferred_round = preferred_round
        self.committed = committed
        # when self is leader
        self.votes = votes
        self.dict_key = node_name

    def __eq__(self, other):
        if self.statue_round == other.statue_round and \
                self.node_name == other.node_name and \
                self.highest_qc == other.highest_qc and \
                self.highest_qc_round == other.highest_qc_round and \
                self.last_voted_round == other.lasted_voted_round and \
                self.preferred_round == other.preferred_round and \
                self.committed == other.committed and \
                self.votes == other.votes:
            return True
        else:
            return False
