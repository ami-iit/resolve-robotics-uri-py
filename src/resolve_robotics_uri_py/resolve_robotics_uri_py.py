import argparse
import os
import pathlib
import sys
import warnings
from typing import Iterable

# =====================
# URI resolving helpers
# =====================

# Supported URI schemes
SupportedSchemes = {"file", "package", "model"}

# Environment variables in the search path.
#
# * https://github.com/robotology/idyntree/issues/291
# * https://github.com/gazebosim/sdformat/issues/1234
#
# AMENT_PREFIX_PATH is the only "special" as we need to add
# "share" after each value, see https://github.com/stack-of-tasks/pinocchio/issues/1520
#
# This list specify the origin of each env variable:
#
# * AMENT_PREFIX_PATH:        Used in ROS2
# * GAZEBO_MODEL_PATH:        Used in Gazebo Classic
# * GZ_SIM_RESOURCE_PATH:     Used in Gazebo Sim >= 7
# * IGN_GAZEBO_RESOURCE_PATH: Used in Ignition Gazebo <= 7
# * ROS_PACKAGE_PATH:         Used in ROS1
# * SDF_PATH:                 Used in sdformat
#
SupportedEnvVars = {
    "AMENT_PREFIX_PATH",
    "GAZEBO_MODEL_PATH",
    "GZ_SIM_RESOURCE_PATH",
    "IGN_GAZEBO_RESOURCE_PATH",
    "ROS_PACKAGE_PATH",
    "SDF_PATH",
}


# Function inspired from https://github.com/ami-iit/robot-log-visualizer/pull/51
def get_search_paths_from_envs(env_list: Iterable[str]) -> list[pathlib.Path]:
    # Read the searched paths from all the environment variables
    search_paths = [
        pathlib.Path(f) if (env != "AMENT_PREFIX_PATH") else pathlib.Path(f) / "share"
        for env in env_list
        if os.getenv(env) is not None
        for f in os.getenv(env).split(os.pathsep)
    ]

    # Resolve and remove duplicate paths
    search_paths = list({path.resolve() for path in search_paths})

    # Keep only existing paths
    existing_search_paths = [path for path in search_paths if path.is_dir()]

    # Notify the user of non-existing paths
    if len(set(search_paths) - set(existing_search_paths)) > 0:
        msg = "resolve-robotics-uri-py: Ignoring non-existing paths from env vars: {}."
        warnings.warn(
            msg.format(
                pathlist_list_to_string(set(search_paths) - set(existing_search_paths))
            )
        )

    return existing_search_paths


def pathlist_list_to_string(path_list: Iterable[str | pathlib.Path]) -> str:
    return " ".join(str(path) for path in path_list)


# ===================
# URI resolving logic
# ===================


def resolve_robotics_uri(uri: str, extra_path: str | None = None) -> pathlib.Path:
    """
    Resolve a robotics URI to an absolute filename.

    Args:
        uri: The URI to resolve.
        extra_path: Additional environment variable to look for the file.

    Returns:
        The absolute filename corresponding to the URI.

    Raises:
        FileNotFoundError: If no file corresponding to the URI is found.
    """

    extra_path = extra_path or ""

    # If the URI has no scheme, use by default file:// which maps the resolved input
    # path to a URI with empty authority
    if not any(uri.startswith(scheme) for scheme in SupportedSchemes):
        uri = f"file://{pathlib.Path(uri).resolve()}"

    # ================================================
    # Process file:/ separately from the other schemes
    # ================================================

    # This is the file URI scheme as per RFC8089:
    # https://datatracker.ietf.org/doc/html/rfc8089

    if uri.startswith("file:"):
        # Strip the scheme from the URI
        uri = uri.replace(f"file://", "")
        uri = uri.replace(f"file:", "")

        # Create the file path, resolving symlinks and '..'
        uri_file_path = pathlib.Path(uri).resolve()

        # Check that the file exists
        if not uri_file_path.is_file():
            msg = "resolve-robotics-uri-py: No file corresponding to URI '{}' found"
            raise FileNotFoundError(msg.format(uri))

        return uri_file_path.resolve()

    # =========================
    # Process the other schemes
    # =========================

    # Get scheme from URI
    from urllib.parse import urlparse

    # Parse the URI
    parsed_uri = urlparse(uri)

    # We only support the following URI schemes at the moment:
    #
    # * file:/      to pass an absolute file path directly
    # * model://    SDF-style model URI
    # * package://  ROS-style package URI
    #
    if parsed_uri.scheme not in SupportedSchemes:
        msg = "resolve-robotics-uri-py: Passed URI '{}' use non-supported scheme '{}'"
        raise FileNotFoundError(msg.format(uri, parsed_uri.scheme))

    # Strip the scheme from the URI
    uri_path = uri
    uri_path = uri_path.replace(f"{parsed_uri.scheme}://", "")

    # List of matching resources found
    model_filenames = []

    # Search the resource in the path from the env variables
    for folder in set(get_search_paths_from_envs(SupportedEnvVars | {extra_path})):

        # Join the folder from environment variable and the URI path
        candidate_file_name = pathlib.Path(folder) / uri_path

        # Expand or resolve the file path (symlinks and ..)
        candidate_file_name = candidate_file_name.resolve()

        if not candidate_file_name.is_file():
            continue

        # Skip if the file is already in the list
        if candidate_file_name not in model_filenames:
            model_filenames.append(candidate_file_name)

    if len(model_filenames) == 0:
        msg = "resolve-robotics-uri-py: No file corresponding to URI '{}' found"
        raise FileNotFoundError(msg.format(uri))

    if len(model_filenames) > 1:
        msg = "resolve-robotics-uri-py: "
        msg += "Multiple files ({}) found for URI '{}', returning the first one."
        warnings.warn(msg.format(pathlist_list_to_string(model_filenames), uri))

    if len(model_filenames) >= 1:
        assert model_filenames[0].exists()
        return pathlib.Path(model_filenames[0]).resolve()


def main():
    parser = argparse.ArgumentParser(
        description="Utility resolve a robotics URI ({}) to an absolute filename.".format(
            ", ".join(f"{scheme}://" for scheme in SupportedSchemes)
        )
    )
    parser.add_argument("uri", metavar="URI", type=str, help="URI to resolve")
    parser.add_argument(
        "--extra_path",
        metavar="PATH",
        type=str,
        help="Additional environment variable to look for the file",
        default=None,
    )

    args = parser.parse_args()

    try:
        result = resolve_robotics_uri(args.uri, args.extra_path)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(result, file=sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
