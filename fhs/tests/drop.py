from fhs.node import FHSNode
from fhs.storage import SyncStorage
from scheduler.NodeFailureSettings import NodeFailure
from sim.message import Message

if __name__ == '__main__':
    sync_storage = SyncStorage()
    failure = NodeFailure(4, 4)
    A = FHSNode(4, None, sync_storage)
    B = FHSNode(4, None, sync_storage)

    a = Message().is_to_drop(A, B, [failure])
    print(a)