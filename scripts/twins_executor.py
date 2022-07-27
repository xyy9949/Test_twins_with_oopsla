import json
import operator
import sys
from copy import deepcopy
sys.path.append('/home/XieYiYang/test_twins_with_oopsla/')
from scheduler.SaveState import *
from os.path import join
import argparse
import simpy
from json import load, dumps
import logging
from fhs.storage import SyncStorage
from fhs.node import FHSNode
from twins.twins import TwinsNetwork, TwinsLE
from sim.network import SyncModel
from scheduler.NodeFailureSettings import NodeFailureSettings
from scheduler.NodeFailureSettings import NodeFailure
from streamlet.node import StreamletNode
import time


class TwinsRunner:
    def __init__(self, num_of_rounds, file_path, NodeClass, node_args, log_path=None):
        self.safety_check = None
        self.depth = None
        self.file_path = file_path
        self.log_path = log_path
        self.NodeClass = NodeClass
        self.node_args = node_args
        self.last_dict_set = dict()
        self.new_dict_set = dict()
        self.fail_states_dict_set = dict()
        self.focus_tags = None
        # TODO:
        self.pre_pick_num = 5

        with open(file_path) as f:
            data = load(f)

        self.num_of_nodes = data['num_of_nodes']
        self.num_of_twins = data['num_of_twins']
        self.scenarios = data['scenarios']
        # how many rounds in one phase
        self.num_of_rounds = num_of_rounds
        self.seed = None
        self.failures = None
        self.print_log_times = 0
        logging.debug(f'Scenario file {args.path} successfully loaded.')
        logging.info(
            f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} twins, '
            f'and {len(self.scenarios)} scenarios.'
        )

    def run(self, tags, T1):
        self.focus_tags = tags
        self.run_over_flag = False
        self.round_state_num = list()

        model = SyncModel()
        network = TwinsNetwork(
            None, model, self.num_of_twins, self.num_of_rounds
        )

        nodes = [self.NodeClass(i, network, *self.node_args)
                 for i in range(self.num_of_nodes + self.num_of_twins)]
        [n.set_le(TwinsLE(n, network, [0, 4])) for n in nodes]
        [network.add_node(n) for n in nodes]

        for i in range(3, self.num_of_rounds + 1):
            if i == 8 or self.run_over_flag:
                break
            runner.run_one_round(i, network)

    def run_one_round(self, current_round, network):
        # list of list
        node_failure_setting = NodeFailureSettings(self.num_of_nodes + self.num_of_twins, 2, current_round)
        self.failures = node_failure_setting.failures

        if current_round == 3:
            self.init_dict_set()

        while self.last_dict_set.__len__() != 0:
            for j, phase_state in enumerate(self.last_dict_set.values()):
                # TODO: only run pre_pick_num times
                if j >= self.pre_pick_num:
                    break
                # TODO: get tmp_round
                if phase_state.node_state_dict.__len__() == 0:
                    tmp_round = 3
                else:
                    tmp_round = phase_state.node_state_dict[0].round

                for i, failure in enumerate(self.failures):
                    self.init_network_nodes(network, phase_state, tmp_round)
                    # run one phase
                    network.failure = failure
                    network.env = simpy.Environment()
                    network.run(150, tmp_round)
                    self.fix_none_state(network)

                    # TODO: calculate vote_abs or is_bk_same
                    if tmp_round % 2 == 1:
                        self.get_votes_abs(network.node_states)
                    else:
                        self.get_is_bk_same(network.node_states)
                    new_phase_state = deepcopy(network.node_states)
                    new_phase_state.sync_storage = deepcopy(next(iter(network.nodes.values())).sync_storage)
                    """ add states_safety_check and store the safety check failure states """
                    if self.duplicate_checking(self.new_dict_set, new_phase_state) is False:
                        print(new_phase_state.to_key(self.focus_tags))
                        if self.states_safety_check(new_phase_state) is True:
                            # TODO: do not need to add to the dict if round = 7
                            if tmp_round < 7:
                                self.new_dict_set.setdefault(new_phase_state.to_key(self.focus_tags), new_phase_state)
                        else:
                            self.fail_states_dict_set.setdefault(new_phase_state.to_key(self.focus_tags), new_phase_state)
                            # TODO: quit once find safety violating
                            self.run_over_flag = True
                    # if self.log_path is not None and self.states_safety_check(new_phase_state) is False:
                    #     file_path = join(self.log_path, f'round-{tmp_round}-state-{j}-failure-{i}.log')
                    #     self.run_over_flag = True
                    #     if self.print_log_times <= 99:
                    #         self._print_log(file_path, network)
                    #         self.print_log_times += 1
                    # for n in network.nodes.values():
                    #     n.log.__init__()
                    logging.info(
                        f'-focustags-{self.focus_tags}-round-{tmp_round}-used_state-{j}/{len(self.last_dict_set)}-failure-{i} finished.There are already'
                        f' {len(self.new_dict_set)} legal states and {len(self.fail_states_dict_set)} safety-violating states.')
                    network.node_states = PhaseState()
                    network.trace = []

                    if self.run_over_flag:
                        break
                if self.run_over_flag:
                    break

            # TODO: turn dict to list to sort(according to votes_abs or is_bk_same)
            tuplelist = list(self.new_dict_set.items())
            if tuplelist.__len__() != 0:
                tmp_round = tuplelist[0][1].node_state_dict[0].round
                if tmp_round % 2 == 0:
                    tuplelist.sort(key=lambda x: x[1].votes_abs)
                else:
                    tuplelist.sort(key=lambda x: x[1].is_bk_same)
            # TODO: put the new dict
            self.last_dict_set = dict(dict(tuplelist), **self.last_dict_set)

            # self._print_state(join(self.log_path, f'round-{current_round}-generate-states-num.log'))
            self.round_state_num.append(len(self.new_dict_set))
            str_tags = ''.join(self.focus_tags)
            T2 = time.time()
            if self.run_over_flag:
                self.print_states_in_every_round(join(self.log_path, f'tags-{str_tags}-find safety-violating-spend time-{T2 - T1}'))
                break
            # else:
            #     self.print_states_in_every_round(join(self.log_path, f'tags-{str_tags}-do not find safety-violating-spend time-{T2 - T1}'))

            # self.new_dict_set = dict()
            # self.fail_states_dict_set = dict()

    def duplicate_checking(self, dict_set, new_phase_state):
        if dict_set.get(new_phase_state.to_key(self.focus_tags)) is not None:
            return True
        else:
            return False

    def init_dict_set(self):
        self.last_dict_set = dict()
        ps = PhaseState()
        self.last_dict_set.setdefault(ps.to_key(self.focus_tags), PhaseState())

    def fix_none_state(self, network):
        # phase state is dict of NodeState
        node_state_dict = network.node_states.node_state_dict
        if isinstance(node_state_dict, dict):
            for index in range(len(network.nodes)):
                node_state = node_state_dict.get(index)
                if node_state is None:
                    node = network.nodes.get(index)
                    none_state = NodeState(node.round, node.name, node.highest_qc,
                                           node.highest_qc_round, node.last_voted_round, node.preferred_round,
                                           node.storage.committed, node.storage.votes, None)
                    node_state_dict.update({node.name: none_state})

    def init_network_nodes(self, network, phase_state, current_round):
        if current_round == 3:
            for x in network.nodes.values():
                x.last_voted_round = 2
                x.round = 3
            return
        for x in network.nodes.values():
            x_state = phase_state.node_state_dict.get(x.name)
            self.set_node_state(x, x_state)
            x.has_message_to_send_flag = False
            x.sync_storage = phase_state.sync_storage

    def set_node_state(self, node, node_state):
        # follower may not save state when it's a vote round
        # A vote round change leader's state
        node.round = node_state.round
        node.highest_qc = node_state.highest_qc
        node.highest_qc_round = node_state.highest_qc_round
        node.last_voted_round = node_state.last_voted_round
        node.preferred_round = node_state.preferred_round
        node.storage.committed = deepcopy(node_state.committed)
        node.storage.votes = deepcopy(node_state.votes)
        node.message_to_send = deepcopy(node_state.message_to_send)

    def print_states_in_every_round(self, file_path):
        data = [f'The state number generated in every round is:\n\n']
        for i, num in enumerate(self.round_state_num):
            data += [f'round{i + 3}-{num}states_num\n']
        with open(file_path, 'w') as f:
            f.write(''.join(data))

    def _print_state(self, file_path):
        phase_state_set = self.new_dict_set
        fail_phase_state_set = self.fail_states_dict_set
        phase_state_list = list(phase_state_set.values())
        fail_phase_state_list = list(fail_phase_state_set.values())
        num = len(self.new_dict_set)
        fail_num = len(self.fail_states_dict_set)
        data = [f'All phases of this round end, found {fail_num} safety-violating states and '
                f'generated {num} legal states.\n##################################\nThe following are top 10 of {fail_num} safety'
                f'-violating states:\n\n']
        dicts = ''
        fail_dicts = ''
        for i, phase_state in enumerate(fail_phase_state_list):
            if isinstance(phase_state.node_state_dict, dict):
                fail_dicts += f'#{i}\n'
                fail_dicts += phase_state.to_string(self.focus_tags)
                # if i != len(fail_phase_state_list) - 1:
                #     fail_dicts += ';\n'
                if i != 9:
                    fail_dicts += '\n'
                if i == 9:
                    break
        data += [fail_dicts]
        data += [f'\n##################################\nThe following are top 10 of {num} legal states:\n\n']
        for i, phase_state in enumerate(phase_state_list):
            if isinstance(phase_state.node_state_dict, dict):
                dicts += f'#{i}\n'
                dicts += phase_state.to_string(self.focus_tags)
                # if i != len(phase_state_list) - 1:
                #     dicts += ';\n'
                if i != 9:
                    dicts += '\n'
                if i == 9:
                    break
        data += [dicts]

        with open(file_path, 'w') as f:
            f.write(''.join(data))

    def _print_log(self, file_path, network):
        data = [f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} ']
        data += [f'twins, and {self.num_of_rounds} rounds.']

        data += ['\n\nfailures:\n[']
        failures = ''
        for i, fai in enumerate(network.failure):
            if isinstance(fai, NodeFailure):
                failures += fai.__str__()
                if i != len(network.failure) - 1:
                    failures += ','
        data += [failures]
        # if failures == '':
        #     logging.info(f'Failures: None')
        # else:
        #     logging.info(f'Failures: {failures}')

        data += [']\n']

        # data += ['\n\nNetwork logs:\n']
        # data += [f'{t}\n' for t in network.trace] + ['\n']

        for n in network.nodes.values():
            data += [f'\n\nNode{n.name} logs:\n']
            data += [f'{t}\n' for t in n.log.log]
            data += [f'\n{n.storage.__repr__()}']

        with open(file_path, 'w') as f:
            f.write(''.join(data))

    def states_safety_check(self, new_phase_state):
        longest = None
        dic = new_phase_state.node_state_dict
        for k, v in dic.items():
            if k == 0 or k == 4: continue
            committed_blocks = v.committed
            committed_list = list(sorted(committed_blocks, key=lambda x: x.for_sort()))
            if longest is None:
                longest = committed_list
                continue
            for i in range(min(len(longest), len(committed_list))):
                if longest[i].round == committed_list[i].round:
                    if str(longest[i]) != str(committed_list[i]):
                        return False
            if len(longest) < len(committed_list):
                longest = committed_list
        return True

    def check_safety(self, network):
        longest = None
        for i in network.nodes:
            if i == 0:
                continue
            if i == 4:
                break
            committed_blocks = network.nodes[i].storage.committed
            committed_list = list(sorted(committed_blocks, key=lambda x: x.for_sort()))
            # print(committed_list[0])
            if longest is None:
                longest = committed_list
                continue
            for i in range(min(len(longest), len(committed_list))):
                if longest[i].round == committed_list[i].round:
                    if str(longest[i]) != str(committed_list[i]):
                        return False
            if len(longest) < len(committed_list):
                longest = committed_list
        return True

    def get_votes_abs(self, node_state):
        bh1 = None
        count = 0
        for i, phase_state in enumerate(node_state.node_state_dict.values()):
            if phase_state.message_to_send is not None:
                block_hash = phase_state.message_to_send[0].block_hash
                if bh1 is None:
                    bh1 = block_hash
                    count += 1
                elif block_hash == bh1:
                    count += 1
                else:
                    count -= 1
        node_state.votes_abs = abs(count)

    def get_is_bk_same(self, node_state):
        bh1 = None
        for i, phase_state in enumerate(node_state.node_state_dict.values()):
            if len(phase_state.message_to_send) > 0:
                block_hash = str(phase_state.message_to_send[0].qc)
                if bh1 is None:
                    bh1 = block_hash
                elif block_hash == bh1:
                    node_state.is_bk_same = 1
                else:
                    node_state.is_bk_same = 0
            if i == 1:
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Twins Executor.')
    parser.add_argument('--num_of_protocol', help='num of protocol')
    parser.add_argument('--depth', help='depth')
    parser.add_argument('--seed', help='seed')
    parser.add_argument('--path', help='path to the scenario file')
    parser.add_argument('--log', help='output log directory')
    parser.add_argument('--v', action='store_true', help='verbose logging')
    parser.add_argument('--focus', help='tag num list')
    args = parser.parse_args()

    args.v = True

    logging.basicConfig(
        level=logging.DEBUG if args.v else logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    sync_storage = SyncStorage()
    rounds_of_protocol = int(args.num_of_protocol)
    runner = TwinsRunner(rounds_of_protocol, args.path, FHSNode, [sync_storage], log_path=args.log)

    # how many failures in one scenario
    runner.depth = int(args.depth)
    # random seed
    runner.seed = int(args.seed)
    runner.focus_tags = args.focus.split(',')  # num list


    runner.focus_tags_list = list()
    ll = ['1', '2', '3', '4', '5', '6', '7']
    for i in range(1, 8):
        if i == 1:
            continue
            for j in range(7):
                new_l = [ll[j]]
                runner.focus_tags_list.append(new_l)
        elif i == 2:
            continue
            for j in range(7):
                for k in range(j + 1, 7):
                    new_l = [ll[j], ll[k]]
                    runner.focus_tags_list.append(new_l)
        elif i == 3:
            continue
            for j in range(7):
                for k in range(j + 1, 7):
                    for l in range(k + 1, 7):
                        if j == 0 and k == 1 and l != 6:
                            continue
                        new_l = [ll[j], ll[k], ll[l]]
                        runner.focus_tags_list.append(new_l)
        elif i == 4:
            continue
            for j in range(7):
                for k in range(j + 1, 7):
                    for l in range(k + 1, 7):
                        for m in range(l + 1, 7):
                            new_l = [ll[j], ll[k], ll[l], ll[m]]
                            runner.focus_tags_list.append(new_l)
        elif i == 5:
            continue
            for j in range(7):
                for k in range(j + 1, 7):
                    for l in range(k + 1, 7):
                        for m in range(l + 1, 7):
                            for n in range(m + 1, 7):
                                new_l = [ll[j], ll[k], ll[l], ll[m], ll[n]]
                                runner.focus_tags_list.append(new_l)
        elif i == 6:
            continue
            for j in range(7):
                for k in range(j + 1, 7):
                    for l in range(k + 1, 7):
                        for m in range(l + 1, 7):
                            for n in range(m + 1, 7):
                                for o in range(n + 1, 7):
                                    new_l = [ll[j], ll[k], ll[l], ll[m], ll[n], ll[o]]
                                    runner.focus_tags_list.append(new_l)
        else:
            new_l = ['1', '2', '3', '4', '5', '6', '7']
            runner.focus_tags_list.append(new_l)

    T1 = time.time()
    runner.run(['1', '2', '3', '4', '5', '6', '7'], T1)
    # runner.focus_tags = args.focus.split(',')  # num list
    # for tags in runner.focus_tags_list:
    #     T1 = time.time()
    #     runner.run(tags, T1)


