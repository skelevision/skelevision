import abc

class Miner(abc.ABC):

    @abc.abstractmethod
    def mine(self, log):
        pass


class LogSkeleton(Miner):

    def mine(self, log):
        pass