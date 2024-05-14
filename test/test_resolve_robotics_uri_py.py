import contextlib
import os
import pathlib
import sys
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

        temp_dir_path = pathlib.Path(temp_dir).resolve()
        temp_dir_path.mkdir(exist_ok=True)
        top_level = temp_dir_path / "top_level.txt"
        top_level.touch(exist_ok=True)

        # Existing relative URI path not in search dirs
        with pytest.raises(FileNotFoundError):
            uri = f"{scheme}top_level.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing absolute URI path in search dirs
        with pytest.raises(FileNotFoundError):
            with export_env_var(name=env_var_name, value=str(temp_dir_path)):
                uri = f"{scheme}/top_level.txt"
                resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing relative URI path in search dirs
        with export_env_var(name=env_var_name, value=str(temp_dir_path)):
            relative_path = "top_level.txt"
            uri = f"{scheme}{relative_path}"
            path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri)
            assert path_of_file == path_of_file.resolve()
            assert path_of_file == temp_dir_path / relative_path

        # Existing relative URI path in search dirs with multiple paths
        with export_env_var(
            name=env_var_name, value=f"/another/dir{os.pathsep}{str(temp_dir_path)}"
        ):
            relative_path = "top_level.txt"
            uri = f"{scheme}{relative_path}"
            path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri)
            assert path_of_file == path_of_file.resolve()
            assert path_of_file == temp_dir_path / relative_path

    # URI path in sub-level search dir
    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir_path = pathlib.Path(temp_dir).resolve()
        level1 = temp_dir_path / "sub" / "level1.txt"
        level1.parent.mkdir(exist_ok=True, parents=True)
        level1.touch(exist_ok=True)

        # Existing relative URI path not in search dirs
        with pytest.raises(FileNotFoundError):
            uri = f"{scheme}sub/level1.txt"
            resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing absolute URI path in search dirs
        with pytest.raises(FileNotFoundError):
            with export_env_var(name=env_var_name, value=str(temp_dir_path)):
                uri = f"{scheme}/sub/level1.txt"
                resolve_robotics_uri_py.resolve_robotics_uri(uri)

        # Existing relative URI path in search dirs
        with export_env_var(name=env_var_name, value=str(temp_dir_path)):
            relative_path = "sub/level1.txt"
            uri = f"{scheme}{relative_path}"
            path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri)
            assert path_of_file == temp_dir_path / relative_path

        # Existing relative URI path in search dirs with multiple paths
        with export_env_var(
            name=env_var_name, value=f"/another/dir{os.pathsep}{str(temp_dir_path)}"
        ):
            relative_path = "sub/level1.txt"
            uri = f"{scheme}{relative_path}"
            path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri)
            assert path_of_file == temp_dir_path / relative_path


def test_scheme_file():

    clear_env_vars()

    # Non-existing absolute URI path
    with pytest.raises(FileNotFoundError):
        uri_file = "file://" + "/this/file/does/not.exist"
        resolve_robotics_uri_py.resolve_robotics_uri(uri_file)

    # Existing absolute URI path with empty authority
    with tempfile.NamedTemporaryFile() as temp:
        temp_name = pathlib.Path(temp.name).resolve(strict=True)
        uri_file = "file://" + temp.name
        path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri_file)
        assert path_of_file == path_of_file.resolve()
        assert path_of_file == temp_name

    # Existing absolute URI path without authority
    with tempfile.NamedTemporaryFile() as temp:
        temp_name = pathlib.Path(temp.name).resolve(strict=True)
        uri_file = "file:" + temp.name
        path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri_file)
        assert path_of_file == path_of_file.resolve()
        assert path_of_file == temp_name

    # Fallback to file:// with no scheme
    with tempfile.NamedTemporaryFile() as temp:
        temp_name = pathlib.Path(temp.name).resolve(strict=True)
        uri_file = f"{temp_name}"
        path_of_file = resolve_robotics_uri_py.resolve_robotics_uri(uri_file)
        assert path_of_file == path_of_file.resolve()
        assert path_of_file == temp_name

    # Try to find an existing file (the Python executable) without any file:/ scheme
    path_of_python_executable = resolve_robotics_uri_py.resolve_robotics_uri(
        sys.executable
    )
    assert path_of_python_executable == pathlib.Path(sys.executable)


def test_additional_search_path():

    clear_env_vars()

    uri = "model://my_model"
    extra_path = "MY_SEARCH_PATH"

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir_path = pathlib.Path(temp_dir).resolve()
        temp_dir_path.mkdir(exist_ok=True)
        top_level = temp_dir_path / "my_model"
        top_level.touch(exist_ok=True)

        # Test resolving a URI with an additional search path
        with export_env_var(name=extra_path, value=str(temp_dir_path)):
            result = resolve_robotics_uri_py.resolve_robotics_uri(uri, extra_path)
            assert result == temp_dir_path / "my_model"

        # Test resolving a URI an additional non-existing search path
        with export_env_var(name=extra_path, value="/this/path/does/not/exist"):
            with pytest.raises(FileNotFoundError):
                resolve_robotics_uri_py.resolve_robotics_uri(uri, extra_path)
