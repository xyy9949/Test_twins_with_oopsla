from copy import copy, deepcopy


class SpecialCopy:
    def __init__(self, ignore_param_list):
        self.ignore_param_list = ignore_param_list

    # ignore copy / no ignore deepcopy
    def special_copy(self, obj):
        new_obj = copy(obj)
        for param_name in obj.__dict__.keys():
            if param_name not in self.ignore_param_list:
                setattr(new_obj, param_name, deepcopy(getattr(obj, param_name)))
        return new_obj
