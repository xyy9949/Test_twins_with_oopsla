class RecommendParam:
    def __init__(self):
        self.param_name_list = list()
        self.old_node_content_dict = dict()

    def compare_node_param(self, new_old_content):
        param_name_list = list()
        old_node_content = self.old_node_content_dict.get(new_old_content.name)
        a = new_old_content.__dict__
        # compare
        b = getattr(new_old_content, "le")

        self.old_node_content_dict.update({new_old_content.name: new_old_content})
        return param_name_list
