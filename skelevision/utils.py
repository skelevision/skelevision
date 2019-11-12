from itertools import combinations
from sortedcontainers import SortedSet

def follows(trace, distance=1):
    if not isinstance(trace, tuple):
        raise ValueError("Trace has to be a tuple of activities.")
    if not float(distance).is_integer():
        raise ValueError("Distance has to be an integer.")
    if not distance >= 1:
        raise ValueError("Distance has to be greater or equal to 1.")

    pairs = dict()

    for i in range(len(trace) - distance):
        ai = trace[i]
        aj = trace[i + distance]

        if (ai, aj) not in pairs:
            pairs[(ai, aj)] = 0

        pairs[(ai, aj)] += 1

    return pairs

def successors(trace):
    if not isinstance(trace, tuple):
        raise ValueError("Trace has to be a tuple of activities.")

    s = dict()

    for pair in combinations(trace, r=2):

        if pair[0] not in s:
            s[pair[0]] = SortedSet()

        s[pair[0]].add(pair[1])

    return s

def predecessors(trace):
    if not isinstance(trace, tuple):
        raise ValueError("Trace has to be a tuple of activities.")

    return successors(tuple(reversed(trace)))