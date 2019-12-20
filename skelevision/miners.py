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

    @staticmethod
    def mine(log, reqA, forbA):
        tl = log.filter_traces(reqA, forbA)

        # Augment the TraceLog object with unique start and end activities
        tl = tl.augment()
        result = {
            "relationships": dict(),
            "statistics": dict()
        }

        # Step 1: Mine equivalence relationship
        result['relationships']['equivalence'] = tl.equivalence()

        # Step 2: Mine always-after relationship
        result['relationships']['alwaysAfter']  = tl.always_after()

        # Step 3: Mine always-before relationship
        result['relationships']['alwaysBefore'] = tl.always_before()

        # Step 4: Mine never-together relationship
        result['relationships']['neverTogether'] = tl.never_together()

        # Step 5: Mine never-together relationship
        result['relationships']['dependency'] = set((tl.follows()).keys())
        
        # Step 6: Statistics
        result['statistics']['dependency'] = tl.follows()
        result['statistics']['sum'] = tl.sum_counter()
        result['statistics']['max'] = tl.max_counter()
        result['statistics']['min'] = tl.min_counter()

        return result
