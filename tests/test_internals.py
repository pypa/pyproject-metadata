import pyproject_metadata


def test_all():
    assert 'typing' not in dir(pyproject_metadata)
