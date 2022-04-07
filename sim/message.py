from scheduler.NodeFailureSettings import NodeFailure


class Message:
    sender = None
    receiver = None

    def set_sender(self, sender):
        self.sender = sender

    def set_receiver(self, receiver):
        self.receiver = receiver

    def is_to_drop(self,current_round,current_phase,failures):
        sender_name = self.sender.name
        receiver_name = self.receiver.name
        k = None
        r = None
        p = None
        for i,setting in enumerate(failures):
            if isinstance(setting, NodeFailure):
                k = setting.k
                r = setting.r
                p = setting.p
            if current_phase == k and current_round == r:
                if sender_name == p or receiver_name == p:
                    return True
        return False

    def verify(self, network):
        return False  # pragma: no cover

    def size(self):
        raise NotImplementedError  # pragma: no cover
