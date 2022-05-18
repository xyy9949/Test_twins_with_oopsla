import json
import sys
from copy import deepcopy

from scheduler.SaveState import *
from sim.Contacts import Contacts

sys.path += '../fhs'
sys.path += '../streamlet'
sys.path += '../twins'
sys.path += '../sim'

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


class TwinsRunner:
    def __init__(self, num_of_rounds, file_path, NodeClass, node_args, log_path=None):
        self.safety_fail_num = None
        self.safety_check = None
        self.depth = None
        self.file_path = file_path
        self.log_path = log_path
        self.NodeClass = NodeClass
        self.node_args = node_args
        self.last_dict_set = set()
        self.new_dict_set = set()

        with open(file_path) as f:
            data = load(f)

        self.num_of_nodes = data['num_of_nodes']
        self.num_of_twins = data['num_of_twins']
        self.scenarios = data['scenarios']
        # how many rounds in one phase
        self.num_of_rounds = num_of_rounds
        self.seed = None
        self.failures = None
        logging.debug(f'Scenario file {args.path} successfully loaded.')
        logging.info(
            f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} twins, '
            f'and {len(self.scenarios)} scenarios.'
        )

    def run(self):
        self.safety_fail_num = 0

        model = SyncModel()
        network = TwinsNetwork(
            None, model, self.num_of_twins, self.num_of_rounds
        )

        nodes = [self.NodeClass(i, network, *self.node_args)
                 for i in range(self.num_of_nodes + self.num_of_twins)]
        [n.set_le(TwinsLE(n, network, [0, 4])) for n in nodes]
        [network.add_node(n) for n in nodes]

        for i in range(3, self.num_of_rounds + 1):
            runner.run_one_round(i, network)
            # todo
            if i == 3:
                break

    def run_one_round(self, current_round, network):
        # list of list
        node_failure_setting = NodeFailureSettings(self.num_of_nodes + self.num_of_twins, 2, current_round)
        self.failures = node_failure_setting.failures

        if current_round == 3:
            self.init_dict_set()

        for j, phase_state in enumerate(self.last_dict_set):
            for i, failure in enumerate(self.failures):
                self.init_network_nodes(network, phase_state.node_state_dict, current_round)
                # run one phase
                network.failure = failure
                network.env = simpy.Environment()
                network.run(150, current_round)
                new_phase_state = deepcopy(network.node_states)
                if self.duplicate_checking(new_phase_state) is False:
                    self.new_dict_set.add(new_phase_state)

                if self.log_path is not None:
                    file_path = join(self.log_path, f'round-{current_round}-state-{j}-failure-{i}.log')
                    self._print_log(file_path, network)

                network.node_states = PhaseState()
                network.trace = []

        self.last_dict_set = self.new_dict_set
        self._print_state(join(self.log_path, f'round-{current_round}-generate-states-num.log'))
        self.new_dict_set = set()

    def duplicate_checking(self, new_phase_state):
        for x in self.new_dict_set:
            if x == new_phase_state:
                return True
        else:
            return False

    def init_dict_set(self):
        self.last_dict_set = set()
        self.last_dict_set.add(PhaseState())

    def init_network_nodes(self, network, node_state_dict, current_round):
        if current_round == 3:
            for x in network.nodes.values():
                x.last_voted_round = 2
                x.round = 3
            return
        for x in network.nodes.values():
            x_state = node_state_dict.get(x.name)
            self.set_node_state(x, x_state)

    def set_node_state(self, node, node_state):
        # follower may not save state when it's a vote round
        # A vote round change leader's state
        if node_state is not None:
            node.round = node_state.round
            node.highest_qc = node_state.highest_qc
            node.highest_qc_round = node_state.highest_qc_round
            node.last_voted_round = node_state.last_voted_round
            node.preferred_round = node_state.preferred_round
            node.storage.committed = deepcopy(node_state.committed)
            node.storage.votes = deepcopy(node_state.votes)
            node.message_to_send = node_state.message_to_send

    def _print_state(self, file_path):
        phase_state_set = self.new_dict_set
        phase_state_list = list(phase_state_set)
        num = len(self.new_dict_set)
        data = [f'All phases of this round end, generated {num} states.\n\nThey are :\n\n']
        dicts = ''
        for i, phase_state in enumerate(phase_state_list):
            if isinstance(phase_state.node_state_dict, dict):
                dicts += phase_state.__str__()
                if i != len(phase_state_list) - 1:
                    dicts += ';\n'
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
        if failures == '':
            logging.info(f'Failures: None')
        else:
            logging.info(f'Failures: {failures}')

        data += [']\n']

        data += ['\n\nNetwork logs:\n']
        data += [f'{t}\n' for t in network.trace] + ['\n']

        for n in network.nodes.values():
            data += [f'\n\nNode{n.name} logs:\n']
            data += [f'{t}\n' for t in n.log.log]
            data += [f'\n{n.storage.__repr__()}']

        with open(file_path, 'w') as f:
            f.write(''.join(data))

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

    runner.run()
