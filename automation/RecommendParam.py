from copy import deepcopy, copy

from special_copy.SpecialCopy import SpecialCopy


class RecommendParam:
    def __init__(self):
        self.changed_param_dict = dict()  # key:param name, value:changing times
        self.old_node_content_dict = dict()
        self.node_param_name_list = list()

    def init_node_param_name_list(self, node):
        self.node_param_name_list = list(node.__dict__.keys())

    def init_changed_param_dict(self):
        for param_name in self.node_param_name_list:
            self.changed_param_dict.update({param_name: 0})

    def compare_node_param(self, new_node_content):
        if new_node_content.timeout != 15:
            a = 1
        old_node_content = self.old_node_content_dict.get(new_node_content.name)
        for param_name in self.node_param_name_list:
            a = getattr(new_node_content, param_name)
            b = getattr(old_node_content, param_name)
            if a != b:
                new_value = self.changed_param_dict.get(param_name) + 1
                self.changed_param_dict.update({param_name: new_value})
        sc = SpecialCopy(None)
        self.old_node_content_dict.update({new_node_content.name: sc.special_copy(new_node_content)})
