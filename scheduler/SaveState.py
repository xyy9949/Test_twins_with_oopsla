class PhaseState:
    def __init__(self):
        self.round = None
        self.node_state_dict = dict()
        self.sync_storage = None
        self.votes_abs = 999
        self.if_bk_same = 1

    def set_votes_abs(self):
        bh1 = None
        count = 0
        for i, node_state in enumerate(self.node_state_dict.values()):
            if node_state.message_to_send is not None:
                block_hash = node_state.message_to_send[0].block_hash
                if bh1 is None:
                    bh1 = block_hash
                    count += 1
                elif block_hash == bh1:
                    count += 1
                else:
                    count -= 1
        self.votes_abs = abs(count)

    def set_if_bk_same(self):
        bh1 = None
        for i, node_state in enumerate(self.node_state_dict.values()):
            if node_state.message_to_send is not None and len(node_state.message_to_send) > 0:
                block_hash = str(node_state.message_to_send[0].qc)
                if bh1 is None:
                    bh1 = block_hash
                elif block_hash == bh1:
                    self.if_bk_same = 1
                else:
                    self.if_bk_same = 0

    def __eq__(self, other):
        if self.node_state_dict.get(0) is None and other.node_state_dict.get(0) is not None:
            return False
        if self.node_state_dict.get(1) is None and other.node_state_dict.get(1) is not None:
            return False
        if self.node_state_dict.get(2) is None and other.node_state_dict.get(2) is not None:
            return False
        if self.node_state_dict.get(3) is None and other.node_state_dict.get(3) is not None:
            return False
        if self.node_state_dict.get(4) is None and other.node_state_dict.get(4) is not None:
            return False
        if self.node_state_dict.get(0) is not None and other.node_state_dict.get(0) is None:
            return False
        if self.node_state_dict.get(1) is not None and other.node_state_dict.get(1) is None:
            return False
        if self.node_state_dict.get(2) is not None and other.node_state_dict.get(2) is None:
            return False
        if self.node_state_dict.get(3) is not None and other.node_state_dict.get(3) is None:
            return False
        if self.node_state_dict.get(4) is not None and other.node_state_dict.get(4) is None:
            return False
        if (self.node_state_dict.get(0) == other.node_state_dict.get(0) or (
                self.node_state_dict.get(0) is None and other.node_state_dict.get(0) is None)) \
                and (self.node_state_dict.get(1) == other.node_state_dict.get(1) or (
                self.node_state_dict.get(1) is None and other.node_state_dict.get(1) is None)) \
                and (self.node_state_dict.get(2) == other.node_state_dict.get(2) or (
                self.node_state_dict.get(2) is None and other.node_state_dict.get(2) is None)) \
                and (self.node_state_dict.get(3) == other.node_state_dict.get(3) or (
                self.node_state_dict.get(3) is None and other.node_state_dict.get(3) is None)) \
                and (self.node_state_dict.get(4) == other.node_state_dict.get(4) or (
                self.node_state_dict.get(4) is None and other.node_state_dict.get(4) is None)):
            return True
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__()

    def __str__(self) -> str:
        return self.node_state_dict.get(0).__str__() \
               + ',' + self.node_state_dict.get(1).__str__() \
               + ',' + self.node_state_dict.get(2).__str__() \
               + ',' + self.node_state_dict.get(3).__str__() \
               + ',' + self.node_state_dict.get(4).__str__()

    def to_string(self, tags) -> str:
        result = 'Node States: \n'
        if self.node_state_dict.get(0) is None:
            result += 'None,\n'
        else:
            result += self.node_state_dict.get(0).to_string(tags)
            result += ',\n'
        if self.node_state_dict.get(1) is None:
            result += 'None,\n'
        else:
            result += self.node_state_dict.get(1).to_string(tags)
            result += ',\n'
        if self.node_state_dict.get(2) is None:
            result += 'None,\n'
        else:
            result += self.node_state_dict.get(2).to_string(tags)
            result += ',\n'
        if self.node_state_dict.get(3) is None:
            result += 'None,\n'
        else:
            result += self.node_state_dict.get(3).to_string(tags)
            result += ',\n'
        if self.node_state_dict.get(4) is None:
            result += 'None,\n'
        else:
            result += self.node_state_dict.get(4).to_string(tags)
            result += '.\n'
        result += 'Sync_storage: \n'
        if self.sync_storage is None:
            result += 'None'
        else:
            for i, item in enumerate(self.sync_storage.blocks.items()):
                result += f'\'{item[0]}\''
                result += ':'
                result += item[1].__repr__()
                if i != len(self.sync_storage.blocks.items()) - 1:
                    result += ',\n'
                else:
                    result += '.\n'
        return result

    def to_key(self, tags) -> str:
        result = ''
        if self.node_state_dict.get(0) is None:
            result += 'None'
        else:
            result += self.node_state_dict.get(0).to_key(tags)
        if self.node_state_dict.get(1) is None:
            result += ',None'
        else:
            result += ','
            result += self.node_state_dict.get(1).to_key(tags)
        if self.node_state_dict.get(2) is None:
            result += ',None'
        else:
            result += ','
            result += self.node_state_dict.get(2).to_key(tags)
        if self.node_state_dict.get(3) is None:
            result += ',None'
        else:
            result += ','
            result += self.node_state_dict.get(3).to_key(tags)
        if self.node_state_dict.get(4) is None:
            result += ',None'
        else:
            result += ','
            result += self.node_state_dict.get(4).to_key(tags)
        result += ','
        if self.sync_storage is None:
            result += 'None.'
        else:
            for i, item in enumerate(self.sync_storage.blocks.items()):
                result += f'\'{item[0]}\''
                result += ':'
                result += item[1].for_key()
                if i != len(self.sync_storage.blocks.items()) - 1:
                    result += ','
                else:
                    result += '.'
        return result


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
                list(sorted(self.highest_qc.votes, key=lambda x: x.author)) == \
                list(sorted(other.highest_qc.votes, key=lambda x: x.author)) and \
                self.highest_qc_round == other.highest_qc_round and \
                self.last_voted_round == other.last_voted_round and \
                self.preferred_round == other.preferred_round and \
                self.votes == other.votes and \
                list(sorted(self.message_to_send, key=lambda x: x.for_sort())) == list(sorted(other.message_to_send, key=lambda x: x.for_sort())) and \
                list(sorted(self.committed, key=lambda x: x.for_sort())) == \
                list(sorted(self.committed, key=lambda x: x.for_sort())):
            return True
        else:
            return False

    def __str__(self):
        return f'NodeState(name:{self.node_name}, round:{self.round}, highest_qc:{self.highest_qc}, ' \
               f'highest_qc_round:{self.highest_qc_round}, last_voted_round:{self.last_voted_round}, ' \
               f'preferred_round:{self.preferred_round}, ' \
               f'committed:{sorted(self.committed, key=lambda x: x.for_sort())}, ' \
               f'message_to_send:{sorted(self.message_to_send, key=lambda x: x.for_sort())})'

    def to_string(self, tags) -> str:
        # 1 round
        # 2 highest_qc
        # 3 highest_qc_round
        # 4 last_voted_round
        # 5 preferred_round
        # 6 committed
        # 7 message_to_send
        result = f'NodeState(name:{self.node_name}'
        if '1' in tags:
            result += f', round:{self.round}'
        if '2' in tags:
            result += f', highest_qc:{self.highest_qc}'
        if '3' in tags:
            result += f', highest_qc_round:{self.highest_qc_round}'
        if '4' in tags:
            result += f', last_voted_round:{self.last_voted_round}'
        if '5' in tags:
            result += f', preferred_round:{self.preferred_round}'
        if '6' in tags:
            result += f', committed:{sorted(self.committed, key=lambda x: x.for_sort())}'
        if '7' in tags:
            if self.message_to_send is None:
                result += f', message_to_send:None'
            else:
                result += f', message_to_send:{sorted(self.message_to_send, key=lambda x: x.for_sort())}'
        result += f')'
        return result

    def to_key(self, tags) -> str:
        # 1 round
        # 2 highest_qc
        # 3 highest_qc_round
        # 4 last_voted_round
        # 5 preferred_round
        # 6 committed
        # 7 message_to_send
        result = f'{self.node_name}'
        if '1' in tags:
            result += f',{self.round}'
        if '2' in tags:
            result += f',{self.highest_qc}'
        if '3' in tags:
            result += f',{self.highest_qc_round}'
        if '4' in tags:
            result += f',{self.last_voted_round}'
        if '5' in tags:
            result += f',{self.preferred_round}'
        if '6' in tags:
            committed = sorted(self.committed, key=lambda x: x.for_sort())
            keys = [i.for_key() for i in committed]
            result += f',{keys}'
        if '7' in tags:
            if self.message_to_send is None:
                result += f',None'
            else:
                message_to_send = sorted(self.message_to_send, key=lambda x: x.for_sort())
                keys = [i.for_key() for i in message_to_send]
                result += f',{keys}'
        return result

    def get_votes_str(self):
        set_dict = self.votes  # dict class set
        new_dict = dict()
        for item in set_dict.items():
            temp = sorted(item[1], key=lambda x: x.author)
            new_dict.setdefault(item[0], temp)
        return new_dict
