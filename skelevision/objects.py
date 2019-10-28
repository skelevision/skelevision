from collections.abc import MutableMapping

from sortedcontainers import SortedSet

from .exceptions import IllegalLogAction


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

    def successors(self, distance=1):
        """Returns a mapping (aka. dict) from pairs of activities to frequency. 
        A pair (a, b) is part of the mapping if activity b follows activity a, 
        at a certain distance, in any of the traces.

        Parameters
        ----------
        distance: int
            Distance two activities have to be appart to be counted in the mapping.
        """
        if not float(distance).is_integer():
            raise ValueError("Distance has to be an integer.")
        if not distance >= 1:
            raise ValueError("Distance has to be greater or equal to 1.")

        pairs = dict()

        for trace in self.__traces:
            for i in range(len(trace) - distance):
                ai = trace[i]
                aj = trace[i + distance]

                if (ai, aj) not in pairs:
                    pairs[(ai, aj)] = 0

                pairs[(ai, aj)] += 1 * self[trace]

        return pairs

    def augment(self, start="[]", end="[>"):
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
