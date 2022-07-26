class PriorityOrdering:
    def __init__(self, current_round, dict):
        self.current_round = current_round
        self.dict = dict
        self.ordered_dict = self.get_ordered_dict()

    def get_ordered_dict(self):
        if self.current_round % 2 == 0:
            return self.get_ordered_dict_vote()
        else:
            return self.get_ordered_dict_block()

    def get_ordered_dict_vote(self):
        self.dict = dict()
        for item in self.dict.items():
            item[0]
        ordered_dict = dict()
        # dict是元素为PhaseState的字典
        # PhaseState是元素为NodeState的字典
        # 全都投了且两种票型数量接近
        return ordered_dict

    def get_ordered_dict_block(self):
        ordered_dict = dict()
        # 全都投了且两种票型数量接近
        return ordered_dict