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
        """Returns a dict, containing the mapping of the strings "relationships" and "statistics"
        to corresponding dict of relationships and statistics

        Parameters
        ----------
        log: `TraceLog`
            tracelog object
        reqA: `set()`
            If one or more of the selected activities
            does not occur in a trace, the entire trace will be filtered out.
        forbA: `set()`
            If one or more of the selected activities
            occurs in a trace, the entire trace will be filtered out.

        Returns
        -------
        `dict`
            mapping of the strings "relationships" and "statistics"
            to corresponding dict of relationships and statistics
        """

        tl = log.filter_traces(reqA, forbA)

        # Augment the TraceLog object with unique start and end activities
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
        result['statistics']['node'] = tl.statistics()
        result['statistics']['link'] = tl.follows()

        return result
