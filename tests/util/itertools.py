from modulecmd.util import groupby


def test_groupby():
    class obj:
        def __init__(self, name):
            self.name = name

    objs = [obj(name) for name in ["a", "b", "c"] for _ in range(3)]
    grouped = groupby(objs, key=lambda x: x.name)
    assert len(grouped) == 3
    assert sorted([_[0] for _ in grouped]) == ["a", "b", "c"]
