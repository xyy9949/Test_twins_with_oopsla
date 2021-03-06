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
        self.depth = self.rand.randint(0, depth)
        self.failures = self.getRandomFailures()
        """ 最多生成depth个failure """


    def getRandomFailures(self):
        if self.depth > 0:
            return self.getBoundedRandomFailures(self.depth)
        else:
            return self.getUnboundedRandomFailures()

    def getBoundedRandomFailures(self, depth):
        f = []
        phases = 0
        failurePerPhase = 0
        # phases = []
        # failurePerPhase = []
        # phases.append(0)
        # failurePerPhase.append(0)
        # for i in range(self.num_phases):
        #     phases.append(i)
        #     i += 1
        # for i in range(self.num_phases):
        #     failurePerPhase.append(0)
        #     i += 1
        round_process = []
        for i in range(self.num_rounds_in_protocol):
            for j in range(self.num_processes):
                round_process.append((i, j))

        for i in range(depth):
            # phaseToFailAt = self.rand.randint(0,len(phases) - 1)
            # phaseToFailAt = self.num_phases
            # failurePerPhase[self.current_phase] += 1
            # failurePerPhase += 1
            # if failurePerPhase[self.current_phase] == self.num_processes:
            #     del phases[phaseToFailAt]
            failureAt = self.rand.randint(0, len(round_process) - 1)
            roundToFail = round_process[failureAt][0]
            processToFail = round_process[failureAt][1]
            del round_process[failureAt]
            # roundToFailAt = random.randint(0,self.num_rounds_in_protocol - 1)
            # processToFail = random.randint(0,self.num_processes - 1)
            nodeFailure = NodeFailure(self.current_phase, roundToFail, processToFail)
            f.append(nodeFailure)
            i += 1
        return f


    def getUnboundedRandomFailures(self):
        return []

class NodeFailure:
    def __init__(self, k, r, p):
        self.k = k
        self.r = r
        self.p = p

    def __str__(self):
        return f'failure (k:{self.k}, r:{self.r}, p:{self.p})'
