import operator
import sys
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
from streamlet.node import StreamletNode


class TwinsRunner:
    def __init__(self, file_path, NodeClass, node_args, log_path=None):
        self.file_path = file_path
        self.log_path = log_path
        self.NodeClass = NodeClass
        self.node_args = node_args

        with open(file_path) as f:
            data = load(f)

        self.num_of_nodes = data['num_of_nodes']
        self.num_of_twins = data['num_of_twins']
        self.scenarios = data['scenarios']
        logging.debug(f'Scenario file {args.path} successfully loaded.')
        logging.info(
            f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} twins, '
            f'and {len(self.scenarios)} scenarios.'
        )

    def run(self):
        self.safety_fail_num = 0

        for i, scenario in enumerate(self.scenarios):
            logging.info(f'Running scenario {i+1}/{len(self.scenarios)}')
            network = runner._run_scenario(scenario)

            # TODO：增加安全性检验：
            self.safety_check = runner.check_safety(network)
            if not self.safety_check:
                self.safety_fail_num = self.safety_fail_num + 1
            # print(safety_check)

            if self.log_path is not None:
                file_path = join(self.log_path, f'{self.file_path}-{i+1}.log')
                runner._print_log(file_path, scenario, network)
                logging.info(f'Log saved in {file_path}')

            # if i == 0:
            #     return
    def _run_scenario(self, scenario):
        logging.debug('1/3 Reading scenario.')
        round_leaders = scenario['round_leaders']
        round_partitions = scenario['round_partitions']
        firewall = scenario['firewall'] if 'firewall' in scenario else {}

        logging.debug('2/3 Setting up network.')
        env = simpy.Environment()
        model = SyncModel()
        network = TwinsNetwork(
            env, model, round_partitions, firewall, self.num_of_twins
        )

        nodes = [self.NodeClass(i, network, *self.node_args)
                 for i in range(self.num_of_nodes + 1)]
        [n.set_le(TwinsLE(n, network, round_leaders)) for n in nodes]
        [network.add_node(n) for n in nodes]

        logging.debug(f'3/3 Executing scenario ({len(round_leaders)} rounds).')
        network.run(until=150)

        return network

    def _print_log(self, file_path, scenario, network):
        data = [f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} ']
        data += [f'twins, and {len(scenario["round_leaders"])} rounds.']
        data += ['\n\nScenario:\n']
        data += [dumps(scenario)]
        # TODO:增加安全性检验：
        data += [f'\n\nSafety check result: {self.safety_check}\n']
        data += [f'\nSafety check failure number: {self.safety_fail_num}\n']

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
            committed_blocks = network.nodes[i].storage.committed
            committed_list = list (sorted(committed_blocks, key = runner.take_round))
            # print(committed_list[0])
            if longest == None:
                longest = committed_list
                continue
            for i in range(min(len(longest), len(committed_list))):
                if longest[i].round == committed_list[i].round:
                    if str(longest[i]) != str(committed_list[i]):
                        return False
            if len(longest) < len(committed_list):
                longest = committed_list
        return True
    def take_round(self, elem):
        return elem.round

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Twins Executor.')
    parser.add_argument('path', help='path to the scenario file')
    parser.add_argument('--log', help='output log directory')
    parser.add_argument('-v', action='store_true', help='verbose logging')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.v else logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    sync_storage = SyncStorage()
    runner = TwinsRunner(args.path, FHSNode, [sync_storage], log_path=args.log)
    #runner = TwinsRunner(args.path, StreamletNode, [], log_path=args.log)
    runner.run()
