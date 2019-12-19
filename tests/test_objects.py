import os

import pytest

from skelevision import TraceLog, IllegalLogAction

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "datasets")


class TestTraceLog(object):
    def test_constructor(self):
        d = {("a", "b", "c"): 2, ("a", "f"): 1}
        tl = TraceLog(d)

        for k, v in d.items():
            assert k in tl
            assert tl[k] == v

        for k, v in tl.items():
            assert k in d
            assert d[k] == v

    def test_labels(self):
        d = {("a", "b", "c"): 2, ("a", "f"): 1}
        labels = ["a", "b", "c", "f"]
        tl = TraceLog(d)

        for a in tl.labels:
            assert a in labels

        for a in labels:
            assert a in tl.labels

    def test_follows(self):
        d = {("a", "b", "c"): 2, ("a", "f"): 1}
        s = {("a", "b"): 2, ("b", "c"): 2, ("a", "f"): 1}
        tl = TraceLog(d)
        s_tl = tl.follows()

        for k, v in s.items():
            assert k in s_tl
            assert s_tl[k] == v

        for k, v in s_tl.items():
            assert k in s
            assert s[k] == v

    def test_follows_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        tl = tl.augment()

        target = {
            ("[>", "a1"): 20,
            ("a1", "a2"): 10,
            ("a1", "a3"): 3,
            ("a1", "a4"): 7,

            ("a2", "a4"): 13,
            ("a2", "a5"): 7,

            ("a3", "a4"): 8,
            ("a3", "a5"): 6,

            ("a4", "a2"): 7,
            ("a4", "a3"): 6,
            ("a4", "a5"): 21,
            
            ("a5", "a6"): 14,
            ("a5", "a7"): 9,
            ("a5", "a8"): 11,

            ("a6", "a2"): 3,
            ("a6", "a3"): 5,
            ("a6", "a4"): 6,

            ("a7", "[]"): 9,
            ("a8", "[]"): 11,

        }

        tl_follows = tl.follows()

        for k, v in target.items():
            assert k in tl_follows
            assert tl_follows[k] == v

        for k, v in tl_follows.items():
            assert k in target
            assert target[k] == v

    def test_follows_distance_2(self):
        d = {("a", "b", "c"): 2, ("a", "f"): 1}
        s = {("a", "c"): 2}
        tl = TraceLog(d)
        s_tl = tl.follows(distance=2)

        for k, v in s.items():
            assert k in s_tl
            assert s_tl[k] == v

        for k, v in s_tl.items():
            assert k in s
            assert s[k] == v

    
    def test_successors_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        tl = tl.augment()

        target = {
            ("[>", "a1"): 20,
            ("a1", "a2"): 10,
            ("a1", "a3"): 3,
            ("a1", "a4"): 7,
            ("a2", "a4"): 13,
            ("a2", "a5"): 7,
            ("a3", "a4"): 8,
            ("a3", "a5"): 6,
            ("a4", "a2"): 7,
            ("a4", "a3"): 6,
            ("a4", "a5"): 21,
            ("a5", "a6"): 14,
            ("a5", "a7"): 9,
            ("a5", "a8"): 11,
            ("a6", "a2"): 3,
            ("a6", "a3"): 5,
            ("a6", "a4"): 6,
            ("a7", "[]"): 9,
            ("a8", "[]"): 11,
        }

        s_tl = tl.follows()

        for k, v in target.items():
            assert k in s_tl
            assert s_tl[k] == v

        for k, v in s_tl.items():
            assert k in target
            assert target[k] == v
            
    def test_follows_loop_len_1(self):
        d = {("a", "b", "c"): 2, ("a", "a", "f"): 1}
        s = {("a", "b"): 2, ("b", "c"): 2, ("a", "f"): 1, ("a", "a"): 1}
        tl = TraceLog(d)
        s_tl = tl.follows(distance=1)

        for k, v in s.items():
            assert k in s_tl
            assert s_tl[k] == v

        for k, v in s_tl.items():
            assert k in s
            assert s[k] == v

    def test_follows_exception_no_integer_distance(self):
        d = {("a", "b", "c"): 2, ("a", "a", "f"): 1}
        tl = TraceLog(d)
        with pytest.raises(ValueError):
            tl.follows(distance=1.2)

    def test_follows_exception_no_positive_integer(self):
        d = {("a", "b", "c"): 2, ("a", "a", "f"): 1}
        tl = TraceLog(d)
        with pytest.raises(ValueError):
            tl.follows(distance=-3.3)

    def test_equivalence_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        target = {("[]", "[>"), ("a1", "[]"), ("a1", "[>"), ("a4", "a5")}
        tl_aug = tl.augment()
        R_eq = tl_aug.equivalence()

        for el in target:
            assert el in R_eq or el[::-1] in R_eq

        for el in R_eq:
            assert el in target or el[::-1] in target

    def test_equivalence_L2(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L2.txt"))
        target = {
            ("[]", "[>"),
            ("a", "[]"),
            ("a", "[>"),
            ("d", "[]"),
            ("d", "[>"),
            ("a", "d"),
            ("b", "c"),
            ("e", "f"),
        }
        tl_aug = tl.augment()
        R_eq = tl_aug.equivalence()

        for el in target:
            assert el in R_eq or el[::-1] in R_eq

        for el in R_eq:
            assert el in target or el[::-1] in target

    def test_equivalence_L4(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L4.txt"))
        target = {("[]", "[>")}
        tl_aug = tl.augment()
        R_eq = tl_aug.equivalence()

        for el in target:
            assert el in R_eq or el[::-1] in R_eq

        for el in R_eq:
            assert el in target or el[::-1] in target

    def test_activity_2_freq(self):
        t = (
            "a1",
            "a2",
            "a4",
            "a5",
            "a6",
            "a3",
            "a4",
            "a5",
            "a6",
            "a4",
            "a3",
            "a5",
            "a6",
            "a2",
            "a4",
            "a5",
            "a7",
        )
        target = {"a1": 1, "a2": 2, "a3": 2, "a4": 4, "a5": 4, "a6": 3, "a7": 1}
        a2f = TraceLog.activity_2_freq(t)
        assert a2f == target

    def test_freq_2_activities(self):
        t = (
            "a1",
            "a2",
            "a4",
            "a5",
            "a6",
            "a3",
            "a4",
            "a5",
            "a6",
            "a4",
            "a3",
            "a5",
            "a6",
            "a2",
            "a4",
            "a5",
            "a7",
        )
        target = {1: {"a1", "a7"}, 2: {"a2", "a3"}, 3: {"a6"}, 4: {"a4", "a5"}}
        f2a = TraceLog.freq_2_activities(t)
        assert f2a == target

    def test_never_together(self):
        d = {
            ("a", "b", "c"): 2,
            ("b", "c", "a"): 1,
            ("a", "c"): 1,
            ("f", "a"): 1,
            ("a",): 2,
        }
        target = {("b", "f"), ("c", "f")}

        tl = TraceLog(d)
        nt = tl.never_together()

        for pair in nt:
            assert pair in target

        for pair in target:
            assert pair in nt

    def test_never_together_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        tl_aug = tl.augment()
        target = {("a7", "a8")}

        nt = tl_aug.never_together()

        for pair in nt:
            assert pair in target

        for pair in target:
            assert pair in nt

    def test_always_after_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        target = {
            ("[>", "a1"),
            ("[>", "a4"),
            ("[>", "a5"),
            ("[>", "[]"),
            ("a1", "a4"),
            ("a1", "a5"),
            ("a1", "[]"),
            ("a2", "a5"),
            ("a2", "[]"),
            ("a3", "[]"),
            ("a3", "a5"),
            ("a4", "a5"),
            ("a4", "[]"),
            ("a5", "[]"),
            ("a6", "a4"),
            ("a6", "a5"),
            ("a6", "[]"),
            ("a7", "[]"),
            ("a8", "[]")
        }
        tl_aug = tl.augment()
        R_aa = tl_aug.always_after()

        for pair in R_aa:
            assert pair in target

        for pair in target:
            assert pair in R_aa

    def test_always_after_xes(self):
        tl = TraceLog.from_xes(os.path.join(DATA, "L2.xes.gz"))
        target = {
            ("[>", "[]"),
            ("[>", "a"),
            ("[>", "b"),
            ("[>", "c"),
            ("[>", "d"),
            ("a", "b"),
            ("a", "c"),
            ("a", "d"),
            ("b", "d"),
            ("c", "d"),
            ("e", "b"),
            ("e", "c"),
            ("e", "d"),
            ("e", "f"),
            ("f", "b"),
            ("f", "c"),
            ("f", "d"),
            ("a", "[]"),
            ("b", "[]"),
            ("c", "[]"),
            ("d", "[]"),
            ("e", "[]"),
            ("f", "[]"),
        }
        tl_aug = tl.augment()
        R_aa = tl_aug.always_after()

        for pair in R_aa:
            assert pair in target

        for pair in target:
            assert pair in R_aa

    def test_always_before_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        target = {
            ("a1", "[>"),
            ("a2", "[>"),
            ("a3", "[>"),
            ("a4", "[>"),
            ("a5", "[>"),
            ("a6", "[>"),
            ("a7", "[>"),
            ("a8", "[>"),
            ("[]", "[>"),
            ("a2", "a1"),
            ("a3", "a1"),
            ("a4", "a1"),
            ("a5", "a1"),
            ("a6", "a1"),
            ("a7", "a1"),
            ("a8", "a1"),
            ("[]", "a1"),
            ("a5", "a4"),
            ("a6", "a4"),
            ("a7", "a4"),
            ("a8", "a4"),
            ("[]", "a4"),
            ("a6", "a5"),
            ("a7", "a5"),
            ("a8", "a5"),
            ("[]", "a5"),
        }
        tl_aug = tl.augment()
        R_ab = tl_aug.always_before()

        for pair in R_ab:
            assert pair in target

        for pair in target:
            assert pair in R_ab

    def test_from_txt(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L2.txt"))
        target = {
            ("a", "b", "c", "d"): 3,
            ("a", "c", "b", "d"): 4,
            ("a", "b", "c", "e", "f", "b", "c", "d"): 2,
            ("a", "b", "c", "e", "f", "c", "b", "d"): 1,
            ("a", "c", "b", "e", "f", "b", "c", "d"): 2,
            ("a", "c", "b", "e", "f", "b", "c", "e", "f", "c", "b", "d"): 1,
        }

        for k, v in target.items():
            assert k in tl
            assert tl[k] == v

        for k, v in tl.items():
            assert k in target
            assert target[k] == v

    def test_from_xes(self):
        tl = TraceLog.from_xes(os.path.join(DATA, "L2.xes"))
        target = {
            ("a", "b", "c", "d"): 3,
            ("a", "c", "b", "d"): 4,
            ("a", "b", "c", "e", "f", "b", "c", "d"): 2,
            ("a", "b", "c", "e", "f", "c", "b", "d"): 1,
            ("a", "c", "b", "e", "f", "b", "c", "d"): 2,
            ("a", "c", "b", "e", "f", "b", "c", "e", "f", "c", "b", "d"): 1,
        }

        for k, v in target.items():
            assert k in tl
            assert tl[k] == v

        for k, v in tl.items():
            assert k in target
            assert target[k] == v

    def test_from_xes_gunzip(self):
        tl = TraceLog.from_xes(os.path.join(DATA, "L2.xes.gz"))
        target = {
            ("a", "b", "c", "d"): 3,
            ("a", "c", "b", "d"): 4,
            ("a", "b", "c", "e", "f", "b", "c", "d"): 2,
            ("a", "b", "c", "e", "f", "c", "b", "d"): 1,
            ("a", "c", "b", "e", "f", "b", "c", "d"): 2,
            ("a", "c", "b", "e", "f", "b", "c", "e", "f", "c", "b", "d"): 1,
        }

        for k, v in target.items():
            assert k in tl
            assert tl[k] == v

        for k, v in tl.items():
            assert k in target
            assert target[k] == v

    def test_from_txt_exception_duplicate_trace(self):
        with pytest.raises(IllegalLogAction):
            tl = TraceLog.from_txt(os.path.join(DATA, "L2_duplicate_trace.txt"))

    def test_from_txt_exception_invalid_frequency(self):
        with pytest.raises(IllegalLogAction):
            tl = TraceLog.from_txt(os.path.join(DATA, "L2_invalid_frequency.txt"))

    def test_augment(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L2.txt"))
        target = {
            ("[>", "a", "b", "c", "d", "[]"): 3,
            ("[>", "a", "c", "b", "d", "[]"): 4,
            ("[>", "a", "b", "c", "e", "f", "b", "c", "d", "[]"): 2,
            ("[>", "a", "b", "c", "e", "f", "c", "b", "d", "[]"): 1,
            ("[>", "a", "c", "b", "e", "f", "b", "c", "d", "[]"): 2,
            ("[>", "a", "c", "b", "e", "f", "b", "c", "e", "f", "c", "b", "d", "[]"): 1,
        }
        tl_aug = tl.augment()

        for k, v in target.items():
            assert k in tl_aug
            assert tl_aug[k] == v

        for k, v in tl_aug.items():
            assert k in target
            assert target[k] == v

    def test_sum_counter_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        tl_aug = tl.augment()
        target = {
            "[]": 20,
            "[>": 20,
            "a1": 20,
            "a2": 20,
            "a3": 14,
            "a4": 34,
            "a5": 34,
            "a6": 14,
            "a7": 9,
            "a8": 11,
        }
        
        count = tl_aug.sum_counter()

        for k, v in count.items():
            assert k in target
            assert target[k] == v

        for a, f in target.items():
            assert a in count
            assert count[a] == f
    
    def test_min_counter_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        tl_aug = tl.augment()
        target = {
            "[]": 1,
            "[>": 1,
            "a1": 1,
            "a2": 0,
            "a3": 0,
            "a4": 1,
            "a5": 1,
            "a6": 0,
            "a7": 0,
            "a8": 0,
        }
        count = tl_aug.min_counter()

        for k, v in count.items():
            assert k in target
            assert target[k] == v

        for a, f in target.items():
            assert a in count
            assert count[a] == f

    def test_max_counter_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        tl_aug = tl.augment()
        target = {
            "[]": 1,
            "[>": 1,
            "a1": 1,
            "a2": 3,
            "a3": 2,
            "a4": 4,
            "a5": 4,
            "a6": 3,
            "a7": 1,
            "a8": 1,
        }
        count = tl_aug.max_counter()

        for k, v in count.items():
            assert k in target
            assert target[k] == v

        for a, f in target.items():
            assert a in count
            assert count[a] == f

    def test_sum_counter_L4(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L4.txt"))
        tl_aug = tl.augment()
        target = {
            "[]": 255,
            "[>": 255,
            "a": 128,
            "b": 127,
            "c": 363,
            "d": 174,
            "e": 81,
        }
        
        count = tl_aug.sum_counter()
        print(count)

        for k, v in count.items():
            assert k in target
            assert target[k] == v

        for a, f in target.items():
            assert a in count
            assert count[a] == f
    
    def test_min_counter_L4(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L4.txt"))
        tl_aug = tl.augment()
        target = {
            "[]": 1,
            "[>": 1,
            "a": 0,
            "b": 0,
            "c": 1,
            "d": 0,
            "e": 0,
        }
        count = tl_aug.min_counter()

        for k, v in count.items():
            assert k in target
            assert target[k] == v

        for a, f in target.items():
            assert a in count
            assert count[a] == f

    def test_max_counter_L4(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L4.txt"))
        tl_aug = tl.augment()
        target = {
            "[]": 1,
            "[>": 1,
            "a": 1,
            "b": 1,
            "c": 2,
            "d": 1,
            "e": 1,
        }
        count = tl_aug.max_counter()

        for k, v in count.items():
            assert k in target
            assert target[k] == v

        for a, f in target.items():
            assert a in count
            assert count[a] == f

    def test_filter_traces(self):
        tl = TraceLog.from_xes(os.path.join(DATA, "L2.xes"))
        
        reqA = {'a', 'b', 'c'}
        forbA = {'e', 'f'}

        # target = {
        #     ('a', 'b', 'c', 'e', 'f', 'b', 'c', 'd') : 2,
        #     ('a', 'b', 'c', 'e', 'f', 'c', 'b', 'd') : 1,
        #     ('a', 'c', 'b', 'e', 'f', 'b', 'c', 'd') : 2,
        #     ('a', 'c', 'b', 'e', 'f', 'b', 'c', 'e', 'f', 'c', 'b', 'd') : 1
        # }

        target = {
            ('a', 'b', 'c', 'd') : 3,
            ('a', 'c', 'b', 'd') : 4
        }

        fa = tl.filter_traces(reqA, forbA)

        for k, v in fa.items():
            assert k, v in target
        
        for k, v in tl.items():
            assert k, v in fa