class RoundSorting:

    def __init__(self, state_dict):
        self.state_dict = state_dict
        self.sorted_state_list = self.get_sorted_dict_round()

    def get_sorted_dict_round(self):
        state_list = list(self.state_dict.values())
        if state_list.__len__() != 0:
            state_list.sort(key=lambda x: x.round, reverse=True)
        return state_list

