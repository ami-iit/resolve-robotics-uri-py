import contextlib
import os
import pathlib
import tempfile
from typing import ContextManager

import pytest

import resolve_robotics_uri_py


def clear_env_vars():
    for env_var in resolve_robotics_uri_py.resolve_robotics_uri_py.SupportedEnvVars:
        _ = os.environ.pop(env_var, None)


@contextlib.contextmanager
def export_env_var(name: str, value: str) -> ContextManager[None]:

    os.environ[name] = value
    yield
    del os.environ[name]


# =======================================
# Test the resolve_robotics_uri functions
# =======================================


@pytest.mark.parametrize("scheme", ["model://", "package://"])
def test_scoped_uri(scheme: str, env_var_name="GZ_SIM_RESOURCE_PATH"):

    clear_env_vars()

    # Non-existing relative URI path
    with pytest.raises(FileNotFoundError):
        uri = f"{scheme}this/package/and/file/does/not.exist"
        resolve_robotics_uri_py.resolve_robotics_uri(uri)

    # Non-existing absolute URI path
    with pytest.raises(FileNotFoundError):
        uri = f"{scheme}/this/package/and/file/does/not.exist"
        resolve_robotics_uri_py.resolve_robotics_uri(uri)

    # Existing URI path not in search dirs
    with pytest.raises(FileNotFoundError):
        with tempfile.NamedTemporaryFile() as temp:
            uri = f"{scheme}{temp.name}"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

    # URI path in top-level search dir
    with tempfile.TemporaryDirectory() as temp_dir:
        pathlib.Path(temp_dir).mkdir(exist_ok=True)
        top_level = pathlib.Path(temp_dir) / "top_level.txt"
        top_level.touch(exist_ok=True)

        # Existing relative URI path not in search dirs
        with pytest.raises(FileNotFoundError):
            uri = f"{scheme}top_level.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing absolute URI path in search dirs
        with pytest.raises(FileNotFoundError):
            with export_env_var(name=env_var_name, value=temp_dir):
                uri = f"{scheme}/top_level.txt"
                resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing relative URI path in search dirs
        with export_env_var(name=env_var_name, value=temp_dir):
            uri = f"{scheme}top_level.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing relative URI path in search dirs with multiple paths
        with export_env_var(name=env_var_name, value=f"/another/dir:{temp_dir}"):
            uri = f"{scheme}top_level.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

    # URI path in sub-level search dir
    with tempfile.TemporaryDirectory() as temp_dir:
        (pathlib.Path(temp_dir) / "sub").mkdir(exist_ok=True)
        level1 = pathlib.Path(temp_dir) / "sub" / "level1.txt"
        level1.touch(exist_ok=True)

        # Existing relative URI path not in search dirs
        with pytest.raises(FileNotFoundError):
            uri = f"{scheme}sub/level1.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing absolute URI path in search dirs
        with pytest.raises(FileNotFoundError):
            with export_env_var(name=env_var_name, value=temp_dir):
                uri = f"{scheme}/sub/level1.txt"
                resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing relative URI path in search dirs
        with export_env_var(name=env_var_name, value=temp_dir):
            uri = f"{scheme}sub/level1.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing relative URI path in search dirs with multiple paths
        with export_env_var(name=env_var_name, value=f"/another/dir:{temp_dir}"):
            uri = f"{scheme}sub/level1.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)


def test_scheme_file():

    clear_env_vars()

    # Non-existing relative URI path
    with pytest.raises(FileNotFoundError):
        uri_file = "file://this/file/does/not.exist"
        resolve_robotics_uri_py.resolve_robotics_uri(uri_file)

    # Non-existing absolute URI path
    with pytest.raises(FileNotFoundError):
        uri_file = "file:///this/file/does/not.exist"
        resolve_robotics_uri_py.resolve_robotics_uri(uri_file)

    # Existing absolute URI path
    with tempfile.NamedTemporaryFile() as temp:
        uri_file = f"file://{temp.name}"
        path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri_file)
        assert path_of_file == pathlib.Path(temp.name)

    # Existing relative URI path (automatic conversion to absolute)
    with tempfile.NamedTemporaryFile() as temp:
        uri_file = f"file:/{temp.name}"
        path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri_file)
        assert path_of_file == pathlib.Path(temp.name)

    # Fallback to file:// with no scheme
    with tempfile.NamedTemporaryFile() as temp:
        uri_file = f"{temp.name}"
        path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri_file)
        assert path_of_file == pathlib.Path(temp.name)
