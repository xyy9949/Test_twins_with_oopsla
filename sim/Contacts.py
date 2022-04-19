class Contacts:
    def __init__(self, compromised, num_of_nodes):
        self.content = self.generate_contacts(compromised, num_of_nodes)

    def set_pseudonym(self, nodes, num_of_nodes):
        for i, node in enumerate(nodes):
            if i >= num_of_nodes:
                node.pseudonym = i % num_of_nodes
            else:
                node.pseudonym = i



    def generate_contacts(self, compromised, num_of_nodes):
        # compromised is like [0,6]
        # num_of_nodes is one number like 7
        # then network become [0,1,2,3,4,5,6,7,8]
        # 0 -> 0,7     6 -> 6,8
        # contacts is like [[0, 7], [1, 8], [2], [3], [4], [5], [6]]
        content = []
        j = 0
        for i in range(0, num_of_nodes):
            addresses = []
            addresses.append(i)
            if i in compromised:
                addresses.append(num_of_nodes + j)
                j += 1
            content.append(addresses)
        return content


# li = [0, 1]
# c = Contacts(list)
# print(c.content)
