import json
import sys
from copy import deepcopy, copy

from automation.RecommendParam import RecommendParam
from sim.Contacts import Contacts
from special_copy.SpecialCopy import SpecialCopy

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
        self.depth = None
        self.file_path = file_path
        self.log_path = log_path
        self.NodeClass = NodeClass
        self.node_args = node_args

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

        for i, scenario in enumerate(self.scenarios):
            self.current_phase = i
            logging.info(f'Running scenario {i + 1}/{len(self.scenarios)}')
            network = runner._run_scenario(scenario, i)

            # TODO：增加安全性检验：
            self.safety_check = runner.check_safety(network)
            if not self.safety_check:
                self.safety_fail_num = self.safety_fail_num + 1

            if self.log_path is not None:
                file_path = join(self.log_path, f'{self.file_path}-{i + 1}.log')
                runner._print_log(file_path, scenario, network)
                logging.info(f'Log saved in {file_path}')

        print(f'Safety check failure number: {self.safety_fail_num}\n')

    def _run_scenario(self, scenario, current_scenario):
        logging.debug('1/3 Reading scenario.')
        round_leaders = scenario['round_leaders']
        firewall = scenario['firewall'] if 'firewall' in scenario else {}

        logging.debug('2/3 Setting up network.')
        env = simpy.Environment()
        model = SyncModel()
        network = TwinsNetwork(
            env, model, firewall, self.num_of_twins, self.num_of_rounds
        )

        """ 重新对该scenario注入failure """
        self.seed = self.seed + 1
        failure_settings = NodeFailureSettings(self.num_of_rounds, current_scenario, self.num_of_nodes + self.num_of_twins, self.depth,
                                               self.seed)
        self.failures = failure_settings.failures
        network.current_phase = current_scenario
        network.failures = self.failures

        """ 改正了原版代码的错误 self.num_of_nodes --> self.num_of_nodes + self.num_of_twins """
        ignore_param_list = ["le", "network", "storage", "rp", "log"]
        # ignore_param_list = ["le", "network", "storage"]
        sc = SpecialCopy(ignore_param_list)
        rp = RecommendParam(sc)
        nodes = [self.NodeClass(i, network, *self.node_args, rp)
                 for i in range(self.num_of_nodes + self.num_of_twins)]
        [n.set_le(TwinsLE(n, network, round_leaders)) for n in nodes]
        [network.add_node(n) for n in nodes]

        for n in nodes:
            rp.old_node_content_dict.update({n.name: sc.special_copy(n)})

        rp.init_node_param_name_list(nodes[0])
        rp.init_changed_param_dict()

        # set pseudonym for nodes
        # compromised = [0]
        # compromised = scenario['compromised']
        # network.contacts = Contacts(compromised, self.num_of_nodes)
        # network.contacts.set_pseudonym(nodes, self.num_of_nodes)

        logging.debug(f'3/3 Executing scenario ({len(round_leaders)} rounds).')
        network.run(until=150)
        for k, v in rp.changed_param_dict.items():
            if v > 0:
                print(k)
        return network

    def _print_log(self, file_path, scenario, network):
        data = [f'Settings: {self.num_of_nodes} nodes, {self.num_of_twins} ']
        data += [f'twins, and {len(scenario["round_leaders"])} rounds.']

        # TODO:增加安全性检验的结果：
        data += [f'\n\nSafety check result: {self.safety_check}\n']
        data += [f'\nSafety check failure number: {self.safety_fail_num}\n']

        data += ['\n\nScenario:\n']
        data += [dumps(scenario)]

        data += ['\n\nfailures:\n']
        failures = ''
        for failure in self.failures:
            if isinstance(failure, NodeFailure):
                failures += '   '
                failures += failure.__str__()
        data += [failures]
        logging.info(f'Failures: {failures}')

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
    parser.add_argument('path', help='path to the scenario file')
    parser.add_argument('--log', help='output log directory')
    parser.add_argument('-v', action='store_true', help='verbose logging')
    args = parser.parse_args()

    args.v = True

    logging.basicConfig(
        level=logging.DEBUG if args.v else logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    sync_storage = SyncStorage()
    # todo
    # need to change when round number change
    rounds_of_protocol = 7
    runner = TwinsRunner(rounds_of_protocol, args.path, FHSNode, [sync_storage], log_path=args.log)

    # how many failures in one scenario
    runner.depth = 5
    # random seed
    runner.seed = 1234567

    runner.run()
