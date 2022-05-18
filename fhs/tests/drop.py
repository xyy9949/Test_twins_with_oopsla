from fhs.messages import Vote
from fhs.node import FHSNode
from fhs.storage import SyncStorage
from scheduler.NodeFailureSettings import NodeFailure
from sim.message import Message

if __name__ == '__main__':
    A = Vote('1||2', 1)
    B = Vote('3||2', 8)

    M = Vote('4||4', 7)
    N = Vote('7||7', 4)

    C = set()
    C.add(A)
    C.add(B)
    D = set()
    D.add(M)
    D.add(N)

    # E = set()
    # E.add('ccccc')
    # E.add('b')
    # E.add('aaa')
    #
    # F = sorted(E, key=lambda x: len(x))


    dict1 = dict()
    dict1.setdefault('1||2', C)
    dict1.setdefault('2||3', D)
    new_dict = dict()

    for item in dict1.items():
        temp = sorted(item[1], key=lambda x: x.author)
        new_dict.setdefault(item[0], temp)

    print(new_dict)