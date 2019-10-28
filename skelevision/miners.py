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
        R_eq = self.__equivalence(tl)
        pass

    def __equivalence(self, log):
        R_eq_trace = dict()

        for trace in log:
            # Extract pairs in current trace
            w = dict()
            f2a = LogSkeleton.__freq_2_activities(trace)
            for s in f2a.values():
                for pair in itertools.product(s, repeat=2):
                    if pair[0] == pair[1]:
                        continue
                    if pair[0] not in w:
                        w[pair[0]] = list()
                    w[pair[0]].append(pair[1])

            # Check if the relationships found till now still hold
            for pair, value in R_eq_trace.items():
                if value:
                    if pair[0] not in w and pair[1] not in w:
                        continue
                    if pair[0] in w and pair[1] not in w[pair[0]]:
                        R_eq_trace[pair] = False
                        R_eq_trace[pair[::-1]] = False

            # Check if there are new values to be added
            for v0, values in w.items():
                for v1 in values: 
                    if (v0, v1) not in R_eq_trace:
                        R_eq_trace[(v0, v1)] = True
            
        # Transform the dict to set
        R_eq = set()
        for pair, value in R_eq_trace.items():
            if value:
                R_eq.add(pair)

        return R_eq

    @staticmethod
    def __activity_2_freq(trace):
        d = {}
        for a in trace:
            if a not in d:
                d[a] = 0
            d[a] += 1

        return d

    @staticmethod
    def __freq_2_activities(trace):
        a2f = LogSkeleton.__activity_2_freq(trace)
        f2a = {}
        for key, value in a2f.items():
            if value not in f2a:
                f2a[value] = set()
            f2a[value].add(key)
        return f2a