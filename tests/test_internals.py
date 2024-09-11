import pyproject_metadata


def test_all() -> None:
    assert 'typing' not in dir(pyproject_metadata)
