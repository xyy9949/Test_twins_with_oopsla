import random


class NodeFailureSettings:
    def __init__(self, num_rounds_in_protocol, current_scenario, num_processes, depth, seed):
        self.num_rounds_in_protocol = num_rounds_in_protocol
        """ 这里的phase就是scenario """
        # self.num_phases = num_phases
        self.current_phase = current_scenario
        self.num_processes = num_processes
        self.num_majority = num_processes / 2 + 1

        self.seed = seed
        self.rand = random.Random(seed)
        self.depth = depth # self.rand.randint(0, depth)
        self.failures = self.getRandomFailures()
        """ 最多生成depth个failure """


    def getRandomFailures(self):
        if self.depth > 0:
            return self.getBoundedRandomFailures(self.depth)
        else:
            return self.getUnboundedRandomFailures()

    def getBoundedRandomFailures(self, depth):
        f = []
        round_process = []
        for i in range(self.num_rounds_in_protocol):
            for j in range(self.num_processes):
                round_process.append((i, j))

        # for i in range(depth):
        #     # no use for failures at round 1 or 2
        #     failure_start_at = 2 * self.num_processes
        #     if failure_start_at == len(round_process) - 1:
        #         break
        #     failureAt = self.rand.randint(failure_start_at, len(round_process) - 1)
        #     roundToFail = round_process[failureAt][0]
        #     processToFail = round_process[failureAt][1]
        #     del round_process[failureAt]
        #     nodeFailure = NodeFailure(self.current_phase, roundToFail + 1, processToFail)
        #     f.append(nodeFailure)
        #     i += 1
        # drop message about node 4
        f.append(NodeFailure(self.current_phase, 3, 0, 4))
        f.append(NodeFailure(self.current_phase, 3, 1, 4))
        f.append(NodeFailure(self.current_phase, 3, 2, 4))
        f.append(NodeFailure(self.current_phase, 3, 3, 4))
        f.append(NodeFailure(self.current_phase, 3, 4, 4))
        f.append(NodeFailure(self.current_phase, 3, 4, 0))
        f.append(NodeFailure(self.current_phase, 3, 4, 1))
        f.append(NodeFailure(self.current_phase, 3, 4, 2))
        f.append(NodeFailure(self.current_phase, 3, 4, 3))
        f.append(NodeFailure(self.current_phase, 3, 4, 4))
        # drop message about node 3
        f.append(NodeFailure(self.current_phase, 4, 3, 0))
        f.append(NodeFailure(self.current_phase, 4, 3, 4))
        # drop message about node 1
        f.append(NodeFailure(self.current_phase, 7, 0, 1))
        f.append(NodeFailure(self.current_phase, 7, 4, 1))
        return f


    def getUnboundedRandomFailures(self):
        return []

class NodeFailure:
    def __init__(self, k, r, sender, receiver):
        self.k = k
        self.r = r
        self.sender = sender
        self.receiver = receiver

    def __str__(self):
        return f'failure (k:{self.k}, r:{self.r}, sender:{self.sender}, receiver:{self.receiver})'
