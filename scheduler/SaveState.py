class PhaseState:
    def __init__(self):
        self.node_state_dict = dict()

    def __eq__(self, other):
        if self.node_state_dict.get(0) == other.node_state_dict.get(0) \
            and self.node_state_dict.get(1) == other.node_state_dict.get(1) \
                and self.node_state_dict.get(2) == other.node_state_dict.get(2) \
                and self.node_state_dict.get(3) == other.node_state_dict.get(3) \
                and self.node_state_dict.get(4) == other.node_state_dict.get(4):
            return True
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__()


class NodeState:
    def __init__(self, round, node_name, highest_qc, highest_qc_round, last_voted_round, preferred_round,
                 committed, votes, message_to_send):
        self.round = round
        self.node_name = node_name
        self.highest_qc = highest_qc
        self.highest_qc_round = highest_qc_round
        self.last_voted_round = last_voted_round
        self.preferred_round = preferred_round
        self.committed = committed
        self.votes = votes
        self.message_to_send = message_to_send
        self.dict_key = node_name

    def __eq__(self, other):
        if self.node_name == other.node_name and \
                self.highest_qc == other.highest_qc and \
                self.highest_qc_round == other.highest_qc_round and \
                self.last_voted_round == other.lasted_voted_round and \
                self.preferred_round == other.preferred_round and \
                self.committed == other.committed and \
                self.votes == other.votes and \
                self.message_to_send == other.message_to_send:
            return True
        else:
            return False
