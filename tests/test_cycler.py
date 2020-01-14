import pytest
from common import utl


def test_empty_cycler():
    with pytest.raises(IndexError):
        c = utl.Cycler([])


def test_cycler():
    items = (2, 4, 42)
    c = utl.Cycler(items)
    assert c.get() == 2  # the first item
    assert c.next() == 4
    assert c.get() == 4
    assert c.next() == 42
    assert c.get() == 42
    assert c.next() == 2
    assert c.get() == 2
    assert c.next() == 4
    assert c.get() == 4

