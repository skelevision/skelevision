import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "datasets")

from skelevision import TraceLog, LogSkeleton


class TestLogSkeleton(object):
    def test_mine(self):
        tl = TraceLog.from_txt(os.path.join(DATA, "L1.txt"))
        miner = LogSkeleton()
        rel, stats = miner.mine(tl)

        target_rel = (
            {("[]", "[>"), ("a1", "[]"), ("a1", "[>"), ("a4", "a5")},
            {
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
                ("a8", "[]"),
            },
            {
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
            },
            {("a7", "a8")},
            {
                ("[>", "a1"),
                ("a1", "a2"),
                ("a1", "a3"),
                ("a1", "a4"),
                ("a2", "a4"),
                ("a2", "a5"),
                ("a3", "a4"),
                ("a3", "a5"),
                ("a4", "a2"),
                ("a4", "a3"),
                ("a4", "a5"),
                ("a5", "a6"),
                ("a5", "a7"),
                ("a5", "a8"),
                ("a6", "a2"),
                ("a6", "a3"),
                ("a6", "a4"),
                ("a7", "[]"),
                ("a8", "[]"),
            },
        )
        target_stats = (
            {
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
            },
            {
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
            },
            {
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
            },
            {
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
            },
        )

        for res, target in zip(rel + stats, target_rel + target_stats):
            if isinstance(res, dict):
                for k, v in res.items():
                    assert k in target
                    assert target[k] == v

                for k, v in target.items():
                    assert k in res
                    assert res[k] == v

            if isinstance(res, set):
                for el in target:
                    assert el in res or el[::-1] in res

                for el in res:
                    assert el in target or el[::-1] in target

        
