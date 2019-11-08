import abc
import itertools


class Miner(abc.ABC):

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def save(self):
        pass

    @abc.abstractmethod
    def mine(self, log):
        pass


class LogSkeleton(Miner):

    def load(self):
        pass

    def save(self):
        pass

    def mine(self, log):
        # Augment the TraceLog object with unique start and end activities
        tl = log.augment()

        # Step 1: Mine equivalence relationship
        R_eq = tl.equivalence()

        # Step 4: Mine never-together relationship
        R_nt = tl.never_together()

        return (R_eq, R_nt)
