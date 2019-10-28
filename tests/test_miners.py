import os

import pytest

from skelevision import TraceLog, IllegalLogAction, LogSkeleton

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "datasets")

class TestLogSkeleton(object):

    def test__equivalence_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        target = {("[]", "[>"), ("a1", "[]"), ("a1", "[>"), ("a4", "a5")}
        tl_aug = tl.augment()
        R_eq = LogSkeleton()._LogSkeleton__equivalence(tl_aug)
        
        for el in target:
            assert el in R_eq or el[::-1] in R_eq

        for el in R_eq:
            assert el in target or el[::-1] in target

    def test__equivalence_L2(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L2.txt"))
        target = {("[]", "[>"), ("a", "[]"), ("a", "[>"), ("d", "[]"), ("d", "[>"), ("a", "d"), ("b", "c"), ("e", "f")}
        tl_aug = tl.augment()
        R_eq = LogSkeleton()._LogSkeleton__equivalence(tl_aug)
        
        for el in target:
            assert el in R_eq or el[::-1] in R_eq

        for el in R_eq:
            assert el in target or el[::-1] in target

    def test__equivalence_L4(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L4.txt"))
        target = {("[]", "[>")}
        tl_aug = tl.augment()
        R_eq = LogSkeleton()._LogSkeleton__equivalence(tl_aug)
        
        for el in target:
            assert el in R_eq or el[::-1] in R_eq

        for el in R_eq:
            assert el in target or el[::-1] in target

    def test__activity_2_freq(self):
        t = ("a1", "a2", "a4", "a5", "a6", "a3", "a4", "a5", "a6", "a4", "a3", "a5", "a6", "a2", "a4", "a5", "a7")
        target = {
            "a1": 1,
            "a2": 2,
            "a3": 2,
            "a4": 4,
            "a5": 4,
            "a6": 3,
            "a7": 1,           
        }
        a2f = LogSkeleton._LogSkeleton__activity_2_freq(t)
        assert a2f == target

    def test__freq_2_activities(self):
        t = ("a1", "a2", "a4", "a5", "a6", "a3", "a4", "a5", "a6", "a4", "a3", "a5", "a6", "a2", "a4", "a5", "a7")
        target = {
            1: {"a1", "a7"},
            2: {"a2", "a3"},
            3: {"a6"},
            4: {"a4", "a5"}
        }
        f2a = LogSkeleton._LogSkeleton__freq_2_activities(t)
        assert f2a == target

    def test__directly_follows_L1(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
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
        tl_aug = tl.augment()
        C_df = LogSkeleton()._LogSkeleton__directly_follows(tl_aug)
        
        assert C_df == target