import gzip
import itertools
import re
import xml.etree.ElementTree as etree
from collections.abc import MutableMapping
from copy import deepcopy
from io import BytesIO

from lxml import etree as etree2
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from sortedcontainers import SortedSet

from .exceptions import IllegalLogAction
from .utils import follows, predecessors, successors


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

    def augment(self, start="[>", end="[]"):
        """Returns a similar TraceLog object where each trace contains an aditional
        start and end activity
        """
        tl = TraceLog()
        for key, value in self.__traces.items():
            trace = (start,) + key + (end,)
            tl[trace] = value
        return tl

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

    def save_to_file(self, filepath, format="txt"):
        """Save a TraceLog object as a `.txt` file.
        """
        if len(self.__traces) == 0:
            return False

        output = ""

        if format == "txt":
            for i, kv in enumerate(self.__traces.items()):
                key = kv[0]
                value = kv[1]
                output += "{}x Case{} {}\n".format(value, i, " ".join(key))

        with open(filepath, "w") as f:
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
        """Returns a set of tuples, representing the pairs of the activities
        which after any occurrence of the first activity the second activity always occurs.

        Returns
        -------
        `set``of `tuples`
            pairs of the activities which after any occurrence of the first activity the
            second activity always occurs.
        """
        pairs = set(itertools.permutations(self.labels, r=2))

        # Remove impossible pairs
        first = "[>"
        last = "[]"
        pairs = set(
            [(a, b) for a, b in pairs if (a, b) != (a, first) and (a, b) != (last, b)]
        )

        for trace in self.__traces:
            s = successors(trace)

            pairs_wc = set(
                [(a, b) for a, b in pairs if a in s.keys() and b not in s[a]]
            )
            pairs = pairs - pairs_wc

        return pairs

    def always_before(self):
        """Returns a set of tuples, representing the pairs of the activities
        which before any occurrence of the first activity the second activity always occurs.

        Returns
        -------
        `set``of `tuples`
            pairs of the activities which before any occurrence of the first activity the
            second activity always occurs.
        """
        pairs = set(itertools.permutations(self.labels, r=2))

        # remove impossible pairs
        first = "[>"
        last = "[]"
        pairs = set(
            [(a, b) for a, b in pairs if (a, b) != (first, b) and (a, b) != (a, last)]
        )

        for trace in self.__traces:
            p = predecessors(trace)

            pairs_wc = set(
                [(a, b) for a, b in pairs if a in p.keys() and b not in p[a]]
            )
            pairs = pairs - pairs_wc

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

    def sum_counter(self):
        """Returns a dict, representing a Mapping from activity to the amount of times the activity
        appears in the TraceLog.

         Parameters
        ----------
        activity: 'str'
            the name of the activity

        Returns
        -------
        'dict'
            Mapping from activity to the amount of times the activity appears in the TraceLog.
        """
        sum_c = dict()

        for trace in self.__traces:
            cur = self.activity_2_freq(trace)
            for k, v in cur.items():
                if k not in sum_c:
                    sum_c[k] = 0
                sum_c[k] += v * self.__traces[trace]

        return sum_c

    def min_counter(self):
        """Returns a dict, representing a Mapping from activity to the min amount of times the
        activity appears in any trace of the TraceLog.

         Parameters
        ----------
        activity: 'str'
            the name of the activity

        Returns
        -------
        'dict'
            Mapping from activity to the min amount of times the activity appears in any trace of the TraceLog.
        """
        base = dict()
        for a in self.labels:
            base[a] = 0
        min_c = dict()
        for trace in self.__traces:
            cur = deepcopy(base)
            cur.update(self.activity_2_freq(trace))
            for k, v in cur.items():
                if k not in min_c:
                    min_c[k] = v
                elif v < min_c[k]:
                    min_c[k] = v
        return min_c

    def max_counter(self):
        """Returns a dict, representing a Mapping from activity to the max amount of times the
        activity appears in any trace of the TraceLog.

         Parameters
        ----------
        activity: 'str'
            the name of the activity

        Returns
        -------
        'dict'
            Mapping from activity to the max amount of times the activity appears in any trace of the TraceLog.
        """
        max_c = dict()
        for trace in self.__traces:
            cur = self.activity_2_freq(trace)
            for k, v in cur.items():
                if k not in max_c:
                    max_c[k] = v
                elif v > max_c[k]:
                    max_c[k] = v
        return max_c

    def filter_traces(self, reqA=None, forbA=None):
        """Filters the tracelog based on required and forbidden activities.

        Parameters
        ----------
        reqA: `set()`
            If one or more of the selected activities
            does not occur in a trace, the entire trace will be filtered out.
        forbA: `set()`
            If one or more of the selected activities
            occurs in a trace, the entire trace will be filtered out.

        Returns
        -------
        `TraceLog`
            Mapping from activity to coresponding event list.
        """
        if reqA is None:
            reqA = []
        if forbA is None:
            forbA = []

        if not isinstance(reqA, list):
            reqA = list(reqA)
        if not isinstance(forbA, list):
            forbA = list(forbA)

        traces = list(self.__traces)

        for trace in traces:

            for a in reqA:
                if a not in trace:
                    traces.remove(trace)
                    break

            for a in forbA:
                if a in trace:
                    traces.remove(trace)
                    break

        filtered_log = TraceLog()
        for trace in traces:
            filtered_log[trace] = self[trace]
            
        return filtered_log

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

    @staticmethod
    def from_xes(filepath):
        file_context = filepath

        if filepath.endswith(".gz"):
            with gzip.open(filepath, "r") as f:
                file_context = BytesIO(f.read())

        context = etree2.iterparse(file_context, events=["start", "end"])

        in_event = False
        tracelog = dict()

        for tree_event, elem in context:
            if elem.tag.endswith("trace"):
                if tree_event == "start":
                    trace = ()
                else:
                    if trace not in tracelog:
                        tracelog[trace] = 0
                    tracelog[trace] += 1

            if elem.tag.endswith("event"):
                in_event = tree_event == "start"

            if (
                in_event
                and "key" in elem.attrib
                and elem.attrib["key"] == "concept:name"
            ):
                if tree_event == "start":
                    trace += (elem.attrib["value"],)

            elem.clear()

        return TraceLog(tracelog)
