import math


class NodeFailureSettings:
    def __init__(self, num_of_processes, num_of_leaders, current_round):
        self.current_round = current_round
        self.num_of_processes = num_of_processes
        self.num_of_leaders = num_of_leaders  # 2
        self.bin_num_len = num_of_leaders * num_of_processes
        """ 最多生成depth个failure """
        self.depth = int(math.pow(2, self.bin_num_len))
        self.failures = self.get_failures()
        # self.failures = self.get_failures_of_twins()

    def get_random_failures(self):
        pass

    def get_failures(self):
        failures = []
        for failure_num in range(self.depth):
            failure = []
            bin_num = bin(failure_num)[2:]
            for j in range(self.bin_num_len - len(bin_num)):
                bin_num = '0' + bin_num
            for i in range(self.bin_num_len):
                flag = bin_num[i]
                if flag == '1':
                    if self.current_round % 2 == 1:
                        # send round
                        sender = int(i / self.num_of_processes)
                        if sender > 0:
                            sender = 4
                        failure.append(
                            NodeFailure(sender,
                                        i % self.num_of_processes))
                    else:
                        # vote round
                        receiver = int(i / self.num_of_processes)
                        if receiver > 0:
                            receiver = 4
                        failure.append(
                            NodeFailure(i % self.num_of_processes,
                                        receiver))
            failures.append(failure)

        return failures

    def get_failures_of_twins(self):
        failures = []
        
        # round 3
        failure = []
        failure.append(NodeFailure(4, 0))
        failure.append(NodeFailure(4, 1))
        failure.append(NodeFailure(0, 2))
        failure.append(NodeFailure(0, 3))
        failure.append(NodeFailure(0, 4))
        failures.append(failure)

        # round 4
        failure = []
        failure.append(NodeFailure(0, 4))
        failure.append(NodeFailure(1, 4))
        failure.append(NodeFailure(2, 0))
        failure.append(NodeFailure(3, 0))
        failure.append(NodeFailure(4, 0))
        failures.append(failure)

        # round 5
        failure = []
        failure.append(NodeFailure(4, 0))
        failure.append(NodeFailure(4, 1))
        failure.append(NodeFailure(4, 2))
        failure.append(NodeFailure(0, 3))
        failure.append(NodeFailure(0, 4))
        failures.append(failure)

        # round 6
        failure = []
        failure.append(NodeFailure(0, 4))
        failure.append(NodeFailure(1, 4))
        failure.append(NodeFailure(2, 4))
        failure.append(NodeFailure(3, 0))
        failure.append(NodeFailure(4, 0))
        failures.append(failure)

        # round 7
        failure = []
        failure.append(NodeFailure(4, 0))
        failure.append(NodeFailure(4, 1))
        failure.append(NodeFailure(0, 2))
        failure.append(NodeFailure(0, 3))
        failure.append(NodeFailure(0, 4))
        failures.append(failure)

        return failures


class NodeFailure:
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

    def __str__(self):
        return f'failure (sender:{self.sender}, receiver:{self.receiver})'
