from copy import copy, deepcopy


class SpecialCopy:
    def __init__(self, ignore_param_list):
        self.ignore_param_list = list()

    def special_copy(self, obj):
        self.ignore_param_list.append("le")
        self.ignore_param_list.append("network")
        self.ignore_param_list.append("storage")
        self.ignore_param_list.append("rp")
        self.ignore_param_list.append("log")
        new_obj = copy(obj)
        for param_name in obj.__dict__.keys():
            if param_name == "network":
                o = getattr(obj, param_name)
                m = getattr(o, "current_phase")
                a = 1
            if param_name not in self.ignore_param_list:
                setattr(new_obj, param_name, deepcopy(getattr(obj, param_name)))
        return new_obj
