import random


class NodeFailureSettings:
    def __init__(self, num_rounds_in_protocol, num_phases, num_processes, depth, seed):
        self.num_rounds_in_protocol = num_rounds_in_protocol
        self.num_phases = num_phases
        self.num_processes = num_processes
        self.num_majority = num_processes / 2 + 1
        self.depth = depth
        self.seed = seed
        self.rand = random.Random(seed)
        self.failures = self.getRandomFailures()

    def getRandomFailures(self):
        if self.depth > 0:
            return self.getBoundedRandomFailures(self.depth)
        else:
            return self.getUnboundedRandomFailures()

    def getBoundedRandomFailures(self, depth):
        f = []
        phases = []
        failurePerPhase = []
        for i in range(self.num_phases):
            phases.append(i)
            i += 1
        for i in range(self.num_phases):
            failurePerPhase.append(0)
            i += 1

        for i in range(depth):
            # phaseToFailAt = self.rand.randint(0,len(phases) - 1)
            phaseToFailAt = 0
            failurePerPhase[phaseToFailAt] += 1
            if failurePerPhase[phaseToFailAt] == self.num_processes:
                del phases[phaseToFailAt]
            roundToFailAt = random.randint(0,self.num_rounds_in_protocol - 1)
            processToFail = random.randint(0,self.num_processes - 1)
            nodeFailure = NodeFailure(phaseToFailAt, roundToFailAt, processToFail)
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
