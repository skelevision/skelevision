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

        # Step 2: Mine always-after relationship
        R_aa = tl.always_after()

        # Step 3: Mine always-before relationship
        R_ab = tl.always_before()

        # Step 4: Mine never-together relationship
        R_nt = tl.never_together()

        # Step 5: Mine never-together relationship
        R_df = set((tl.follows()).keys())
        
        # Step 6: Statistics
        C_df = tl.follows()
        C_sum = tl.sum_counter()
        C_max = tl.max_counter()
        C_min = tl.min_counter()

        return (R_eq, R_aa, R_ab, R_nt, R_df), (C_df, C_sum, C_max, C_min)
