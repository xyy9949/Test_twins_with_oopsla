import json
import sys
from copy import deepcopy
sys.path.append('E:\\bft_testing\\Test_twins_with_oopsla\\scheduler')
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
from collections import deque
from streamlet.node import StreamletNode


class TwinsRunner:
    def __init__(self, num_of_rounds, file_path, NodeClass, node_args, log_path=None):
        self.safety_check = None
        self.depth = None
        self.file_path = file_path
        self.log_path = log_path
        self.NodeClass = NodeClass
        self.node_args = node_args
        self.list_of_dict = []
        self.state_queue = deque()
        self.fail_states_dict_set = dict()
        self.focus_tags = None

        with open(file_path) as f:
            data = load(f)

        self.num_of_nodes = data['num_of_nodes']
        self.num_of_twins = data['num_of_twins']
        self.scenarios = data['scenarios']
        # how many rounds in one phase
        self.num_of_rounds = num_of_rounds
        self.seed = None
        self.failures = None
        self.failed_times = 0
        logging.debug(f'Scenario file {args.path} successfully loaded.')
        logging.info(
            f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} twins, '
            f'and {len(self.scenarios)} scenarios.'
        )

    def run(self):

        model = SyncModel()
        network = TwinsNetwork(
            None, model, self.num_of_twins, self.num_of_rounds
        )

        nodes = [self.NodeClass(i, network, *self.node_args)
                 for i in range(self.num_of_nodes + self.num_of_twins)]
        [n.set_le(TwinsLE(n, network, [0, 4])) for n in nodes]
        [network.add_node(n) for n in nodes]

        runner.run_(network)

    def run_(self, network):
        while len(self.state_queue) != 0:
            phase_state = self.state_queue.popleft()
            current_round = phase_state.round
            node_failure_setting = NodeFailureSettings(self.num_of_nodes + self.num_of_twins, 2, current_round)
            self.failures = node_failure_setting.failures
            for i, failure in enumerate(self.failures):
                self.init_network_nodes(network, phase_state, current_round)
                # run one phase
                network.failure = failure
                network.env = simpy.Environment()
                network.run(150, current_round)
                self.fix_none_state(network)
                new_phase_state = deepcopy(network.node_states)
                new_phase_state.sync_storage = deepcopy(next(iter(network.nodes.values())).sync_storage)
                new_phase_state.round = current_round + 1
                """ add states_safety_check and store the safety check failure states """
                if self.duplicate_checking(self.list_of_dict[current_round], new_phase_state) is False:
                    if self.states_safety_check(new_phase_state) is True:
                        self.list_of_dict[current_round].setdefault(new_phase_state.to_key(self.focus_tags), new_phase_state)
                    else:
                        self.fail_states_dict_set.setdefault(new_phase_state.to_key(self.focus_tags), new_phase_state)

                if self.log_path is not None and self.states_safety_check(new_phase_state) is False:
                    file_path = join(self.log_path, f'failure-violating-{self.failed_times}.log')
                    if self.failed_times <= 99:
                        self._print_log(file_path, network)
                        self.failed_times += 1
                for n in network.nodes.values():
                    n.log.__init__()
                # logging.info(
                #     f'round-{current_round}-used_state-{j}-failure-{i} finished.There are already'
                #     f' {len(self.new_dict)} legal states and {len(self.fail_states_dict_set)} safety-violating states.')
                network.node_states = PhaseState()
                network.trace = []
            self.add_state_queue()
        # self._print_state()
        self.fail_states_dict_set = dict()

    def add_state_queue(self):
        print()

    def duplicate_checking(self, dict_set, new_phase_state):
        if dict_set.get(new_phase_state.to_key(self.focus_tags)) is not None:
            return True
        else:
            return False

    def init_dict_set(self):
        ps = PhaseState()
        self.state_queue.append(ps)

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

    def _print_state(self, file_path):
        # join(self.log_path, f'round-{current_round}-generate-states-num.log')
        phase_state_set = self.list_of_dict[0]
        fail_phase_state_set = self.fail_states_dict_set
        phase_state_list = list(phase_state_set.values())
        fail_phase_state_list = list(fail_phase_state_set.values())
        num = len(self.list_of_dict[0])
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

    for i in range(rounds_of_protocol-2):
        runner.list_of_dict.append(dict())

    # how many failures in one scenario
    runner.depth = int(args.depth)
    # random seed
    runner.seed = int(args.seed)
    runner.focus_tags = args.focus.split(',')  # num list

    runner.run()
