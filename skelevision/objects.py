import itertools
from copy import deepcopy
from collections.abc import MutableMapping

from sortedcontainers import SortedSet

from .exceptions import IllegalLogAction
from .utils import follows, successors, predecessors


class TraceLog(MutableMapping):
    """Representation of a trace log. Works like a base python dict,
    where the keys are tuples denoting individual traces 
    (e.g. '("a", "b", "c")' denoted trace 'abc') and the values 
    denote the frequencies of the traces.         
    """
    
    def __init__(self, *args, **kwargs):
        self.__traces = dict()
        self.__traces.update(*args, **kwargs)
        self.__labels = SortedSet()

        for trace in self.__traces:
            for activity in trace:
                self.__labels.add(activity)

    def __setitem__(self, key, value):
        if not float(value).is_integer() or value < 0:
            raise IllegalLogAction(
                "Cannot set value at key {} equal to {}.".format(key, value)
            )
        self.__traces[key] = value
        # If there is a new activity add it to the set of labels
        for activity in key:
                self.__labels.add(activity)

    def __getitem__(self, key):
        return self.__traces[key]

    def __delitem__(self, key):
        del self.__traces[key]

    def __iter__(self):
        return iter(self.__traces)

    def __len__(self):
        return len(self.__traces)

    def __str__(self):
        """returns simple dict representation of the mapping"""
        return str(self.__traces)

    def __repr__(self):
        """echoes class, id, & reproducible representation in the REPL"""
        return "{}, D({})".format(super(TraceLog, self).__repr__(), self.__traces)

    @property
    def labels(self):
        """Returns all the unique labels of activities in the trace log."""
        return self.__labels

    def follows(self, distance=1):
        """Returns a mapping (aka. dict) from pairs of activities to frequency. 
        A pair (a, b) is part of the mapping if activity b follows activity a, 
        at a certain distance, in any of the traces.

        Parameters
        ----------
        distance: int
            Distance two activities have to be appart to be counted in the mapping.
        """
        pairs = dict()

        for trace in self.__traces:
            # Get the follows mapping only for the current trace
            f = follows(trace, distance=distance)

            # Add all the items to the overall dictionary
            for p, p_freq in f.items():
                # If it's not there yet, add the default value 
                if p not in pairs:
                    pairs[p] = 0
                pairs[p] += p_freq * self.__traces[trace]

        return pairs

    def augment(self, start="[>", end="[]"):
        """Returns a similar TraceLog object where each trace contains an aditional
        start and end activity
        """
        tl = TraceLog()
        for key, value in self.__traces.items():
            trace = (start,) + key + (end, )
            tl[trace] = value
        return tl

    def save_to_file(self, filepath, format='txt'):
        """Save a TraceLog object as a `.txt` file.
        """
        if len(self.__traces) == 0:
            return False

        output = ''

        if format == 'txt':
            for i, kv in enumerate(self.__traces.items()):
                key = kv[0]
                value = kv[1]
                output += '{}x Case{} {}\n'.format(value, i, " ".join(key))
            
        with open(filepath, 'w') as f:
            f.write(output)
        
        return True

    def never_together(self):
        """Returns a set of tuples, representing the pairs of the activities 
        which are never together in any of the traces.
        
        Returns
        -------
        `set` of `tuples`
            the pairs of the activities which are never together in any of the traces
        """

        pairs = set(itertools.combinations(self.labels, r=2))

        for trace in self.__traces:
            trace = SortedSet(trace)
            trace_pairs = list(itertools.combinations(trace, r=2))
            pairs_wc = deepcopy(pairs)

            for pair in pairs:
                if pair in trace_pairs:
                    pairs_wc.discard(pair)

            pairs = pairs_wc

        return pairs

    def equivalence(self):
        """Returns a set of tuples, representing the pairs of the activities
        which are always together in all of the traces the same number of times.
        
        Returns
        -------
        `set``of `tuples`
            the pairs of the activities which are always together in all of the 
            traces the same number of times
        """
        R_eq_trace = dict()

        for trace in self.__traces:
            # Extract pairs in current trace
            w = dict()
            f2a = TraceLog.freq_2_activities(trace)
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

    def always_after(self):
        '''Returns a set of tuples, representing the pairs of the activities
        which after any occurrence of the first activity the second activity always occurs.

        Returns
        -------
        `set``of `tuples`
            pairs of the activities which after any occurrence of the first activity the
            second activity always occurs.
        '''
        pairs = set(itertools.product(self.labels, repeat=2))
        pairs = pairs.difference((x,x) for x in self.__labels)

        for trace in self.__traces:
            s = successors(trace)

            # Remove impossible pairs
            first = trace[0]
            last = trace[-1]
            for a in self.__labels:
                pairs.discard((a, first))
                pairs.discard((last, a))
            
            # Remove pairs that don't respect always after relatioship
            pairs_wc = deepcopy(pairs)
            for pair in pairs:
                if pair[0] in s.keys() and pair[1] not in s[pair[0]]:
                    pairs_wc.discard(pair)
            pairs = pairs_wc
        
        return pairs

    def always_before(self):
        pairs = set(itertools.product(self.labels, repeat=2))
        pairs = pairs.difference((x,x) for x in self.__labels)

        for trace in self.__traces:
            p = predecessors(trace)

            # Remove impossible pairs
            first = trace[0]
            last = trace[-1]
            for a in self.__labels:
                pairs.discard((first, a))
                pairs.discard((a, last))
            
            # Remove pairs that don't respect always after relatioship
            pairs_wc = deepcopy(pairs)
            for pair in pairs:
                if pair[0] in p.keys() and pair[1] not in p[pair[0]]:
                    pairs_wc.discard(pair)
            pairs = pairs_wc
        
        return pairs

    @staticmethod
    def activity_2_freq(trace):
        """For a given trace, return a mapping from activity to frequency in trace.
        
        Parameters
        ----------
        trace: `tuple` of `str`
            a trace as a tuple of activities
        
        Returns
        -------
        `dict`
            mapping from activity to frequency in trace
        """
        d = {}
        for a in trace:
            if a not in d:
                d[a] = 0
            d[a] += 1

        return d

    @staticmethod
    def freq_2_activities(trace):
        """For a given trace, return a mapping from frequency to set of activities, 
        with that frequency in the trace.
        
        Parameters
        ----------
        trace: `tuple` of `str`
            a trace as a tuple of activities
        
        Returns
        -------
        `dict`
            mapping from frequency to `set` activities in trace
        """
        a2f = TraceLog.activity_2_freq(trace)
        f2a = {}
        for key, value in a2f.items():
            if value not in f2a:
                f2a[value] = set()
            f2a[value].add(key)
        return f2a

    @staticmethod
    def from_txt(filepath, delimiter=None, frequency_idx=0, first_activity_idx=2):
        """Parses a `.txt` file containing a trace log and returns a TraceLog object of it.

        Parameters
        ----------
        filepath: path-like
            The path to the `.txt` file.
        delimiter: `str`
            Character delimiting the different values. Default None, thus splitting by all the whitespace.
        frequency_idx: `int`
            Default 0.
        first_activity_idx: `int`
            Default 2.

        Returns
        -------
        `TraceLog`
            Mapping from activity to coresponding event list.
        """
        tl = TraceLog()

        with open(filepath, "r") as f:
            for row in f:

                row = row.strip()
                if len(row) == 0:
                    continue

                parts = row.split(delimiter)
                a = tuple(parts[first_activity_idx:])
                try:
                    frequency = int((parts[frequency_idx]).replace("x", ""))
                except Exception:
                    raise IllegalLogAction("No frequency for trace: {}.".format(a))

                if a in tl:
                    raise IllegalLogAction(
                        "Attempting to add trace {} twice.".format(a)
                    )

                tl[a] = frequency

        return tl
