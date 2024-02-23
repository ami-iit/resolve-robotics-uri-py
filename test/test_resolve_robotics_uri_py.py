import resolve_robotics_uri_py
import pytest


def test_non_existing_file():

    with pytest.raises(FileNotFoundError):
        resolve_robotics_uri_py.resolve_robotics_uri(
            "package://this/package/and/file/does/not.exist"
        )
