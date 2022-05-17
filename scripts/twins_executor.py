import json
import sys
from copy import deepcopy

from scheduler.SaveStatue import *
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

        for i in range(3, self.num_of_rounds):
            runner.run_one_round(i)

    def run_one_round(self, current_round):
        # list of list
        node_failure_setting = NodeFailureSettings(self.num_of_nodes + self.num_of_twins, 2, current_round)
        self.failures = node_failure_setting.failures

        model = SyncModel()
        network = TwinsNetwork(
            None, model, self.num_of_twins, self.num_of_rounds
        )

        if current_round == 3:
            self.init_dict_set()

        if current_round == 4:
            print()

        for j, phase_statue in enumerate(self.last_dict_set):
            for i, failure in enumerate(self.failures):
                self.init_network_nodes(network, phase_statue.node_statue_dict, current_round)
                # run one phase
                network.failure = failure
                network.env = simpy.Environment()
                network.run(150, current_round)
                # todo
                self.new_dict_set.add(deepcopy(network.node_statues))

                if self.log_path is not None:
                    file_path = join(self.log_path, f'round-{current_round}-statue-{j}-failure-{i}.log')
                    self._print_log(file_path, network)

                network.node_statues = PhaseStatue()
                network.trace = []

                if i == 1:
                    break

        self.last_dict_set = self.new_dict_set
        self.new_dict_set = set()

        # do sth with statue set

    def init_dict_set(self):
        self.last_dict_set = set()
        self.last_dict_set.add(PhaseStatue())

    def init_network_nodes(self, network, node_statue_dict, current_round):
        nodes = [self.NodeClass(i, network, *self.node_args)
                 for i in range(self.num_of_nodes + self.num_of_twins)]
        [n.set_le(TwinsLE(n, network, [0, 4])) for n in nodes]
        [network.add_node(n) for n in nodes]
        if current_round == 3:
            return
        for x in network.nodes.values():
            x_statue = node_statue_dict.get(x.name)
            self.set_node_statue(x, x_statue)

    def set_node_statue(self, node, node_statue):
        # follower may not save statue when it's a vote round
        # A vote round change leader's statue
        if node_statue is not None:
            node.round = node_statue.round
            node.highest_qc = node_statue.highest_qc
            node.highest_qc_round = node_statue.highest_qc_round
            node.last_voted_round = node_statue.last_voted_round
            node.preferred_round = node_statue.preferred_round
            node.storage.committed = node_statue.committed
            node.storage.votes = node_statue.votes
            node.message_to_send = node_statue.message_to_send


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
