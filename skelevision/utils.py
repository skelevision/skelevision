from itertools import combinations
from sortedcontainers import SortedSet

def follows(trace, distance=1):
    """Returns a mapping (aka. dict) from pairs of activities to frequency.
    A pair (a, b) is part of the mapping if activity b directly follows activity a,
    in any of the traces.

    Parameters
    ----------
    distance: int
        Distance two activities have to be appart to be counted in the mapping.
    """

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
    """Returns a mapping (aka. dict) from pairs of activities to sets of activities which follows.
    A dict {a: (b, c)} is part of the mapping if activity b and c follows activity a,
    in any of the traces.

    Parameters
    ----------
    trace: TraceLog
        tracelog object

    Returns
    -------
    `SortedSet`
        the pairs of the activities which are the successors in any of the traces
    """

    if not isinstance(trace, tuple):
        raise ValueError("Trace has to be a tuple of activities.")

    s = dict()

    for pair in combinations(trace, r=2):

        if pair[0] not in s:
            s[pair[0]] = SortedSet()

        s[pair[0]].add(pair[1])

    return s

def predecessors(trace):
    """Returns a mapping (aka. dict) from pairs of activities to sets of activities which are followd by.
    A dict {a: (b, c)} is part of the mapping if activity b and c followed by activity a,
    in any of the traces.

    Parameters
    ----------
    trace: TraceLog
        tracelog object

    Returns
    -------
    `SortedSet`
        the pairs of the activities which are the successors in any of the traces
    """

    if not isinstance(trace, tuple):
        raise ValueError("Trace has to be a tuple of activities.")

    return successors(tuple(reversed(trace)))