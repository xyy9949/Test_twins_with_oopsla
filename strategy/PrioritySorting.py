class PrioritySorting:

    def __init__(self, current_round, dict):
        self.current_round = current_round
        self.dict = dict
        self.sorted_state_list = self.get_sorted_dict()

    def get_sorted_dict(self):
        if self.current_round % 2 == 0:
            return self.get_sorted_dict_vote()
        else:
            return self.get_sorted_dict_block()

    def get_sorted_dict_vote(self):
        state_list = list(self.dict.values())
        if state_list.__len__() != 0:
            state_list.sort(key=lambda x: x.votes_abs)
        return state_list

    def get_sorted_dict_block(self):
        state_list = list(self.dict.values())
        if state_list.__len__() != 0:
            state_list.sort(key=lambda x: x.if_bk_same)
        # 全都投了且两种票型数量接近
        return state_list
