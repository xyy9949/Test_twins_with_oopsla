from scheduler.NodeFailureSettings import NodeFailure


class Message:
    round = None

    def set_sender(self, sender):
        self.sender = sender

    def set_receiver(self, receiver):
        self.receiver = receiver

    def is_to_drop(self, fromx, tox, failure_list):
        sender_name = fromx.name
        receiver_name = tox.name
        sender = None
        receiver = None
        for i, setting in enumerate(failure_list):
            if isinstance(setting, NodeFailure):
                sender = setting.sender
                receiver = setting.receiver
            if sender_name == sender and receiver_name == receiver:
                return True
        return False

    def verify(self, network):
        return False  # pragma: no cover

    def size(self):
        raise NotImplementedError  # pragma: no cover

    def __hash__(self) -> int:
        return super().__hash__()

