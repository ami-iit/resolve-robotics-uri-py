import argparse
import os
import pathlib
import sys
import warnings

# Supported URI schemes
SupportedSchemes = {"file", "package", "model"}


# Function inspired from https://github.com/ami-iit/robot-log-visualizer/pull/51
def get_search_paths_from_envs(env_list):
    return [
        pathlib.Path(f) if (env != "AMENT_PREFIX_PATH") else pathlib.Path(f) / "share"
        for env in env_list
        if os.getenv(env) is not None
        for f in os.getenv(env).split(os.pathsep)
    ]


def pathlist_list_to_string(path_list):
    return " ".join(str(path) for path in path_list)


def resolve_robotics_uri(uri: str) -> pathlib.Path:
    # List of environment variables to consider, see:
    # * https://github.com/robotology/idyntree/issues/291
    # * https://github.com/gazebosim/sdformat/issues/1234
    # AMENT_PREFIX_PATH is the only "special" as we need to add
    # "share" after each value, see https://github.com/stack-of-tasks/pinocchio/issues/1520
    # This list specify the origin of each env variable:
    # * GAZEBO_MODEL_PATH: Used in Gazebo Classic
    # * ROS_PACKAGE_PATH: Used in ROS1
    # * AMENT_PREFIX_PATH: Used in ROS2
    # * SDF_PATH: Used in sdformat
    # * IGN_GAZEBO_RESOURCE_PATH: Used in Ignition Gazebo <= 7
    # * GZ_SIM_RESOURCE_PATH: Used in Gazebo Sim >= 7
    env_list = [
        "GAZEBO_MODEL_PATH",
        "ROS_PACKAGE_PATH",
        "AMENT_PREFIX_PATH",
        "SDF_PATH",
        "IGN_GAZEBO_RESOURCE_PATH",
        "GZ_SIM_RESOURCE_PATH",
    ]

    # If the URI has no scheme, use by default the file://
    if "://" not in uri:
        uri = f"file://{uri}"

    # Get scheme from URI
    from urllib.parse import urlparse

    # Parse the URI
    parsed_uri = urlparse(uri)

    # We only support the following URI schemes at the moment:
    #
    # * file://:    to pass an absolute file path directly
    # * model://:   SDF-style model URI
    # * package://: ROS-style package URI
    #
    if parsed_uri.scheme not in SupportedSchemes:
        msg = "resolve-robotics-uri-py: Passed URI '{}' use non-supported scheme '{}'"
        raise FileNotFoundError(msg.format(uri, parsed_uri.scheme))

    # Strip the URI scheme
    uri_path = uri.replace(f"{parsed_uri.scheme}://", "")

    if parsed_uri.scheme == "file":
        # Ensure the URI path is absolute
        uri_path = uri_path if uri_path.startswith("/") else f"/{uri_path}"

        # Create the file path
        uri_file_path = pathlib.Path(uri_path)

        # Check that the file exists
        if not uri_file_path.is_file():
            msg = "resolve-robotics-uri-py: No file corresponding to URI '{}' found"
            raise FileNotFoundError(msg.format(uri))

        return uri_file_path

    # List of matching resources found
    model_filenames = []

    for folder in set(get_search_paths_from_envs(env_list)):

        candidate_file_name = folder / uri_path

        if not candidate_file_name.is_file():
            continue

        if candidate_file_name not in model_filenames:
            model_filenames.append(candidate_file_name)

    if len(model_filenames) == 0:
        msg = "resolve-robotics-uri-py: No file corresponding to uri '{}' found"
        raise FileNotFoundError(msg.format(uri))

    if len(model_filenames) > 1:
        msg = "resolve-robotics-uri-py: "
        msg += "Multiple files ({}) found for URI '{}', returning the first one."
        warnings.warn(msg.format(pathlist_list_to_string(model_filenames), uri))

    if len(model_filenames) >= 1:
        assert model_filenames[0].exists()
        return pathlib.Path(model_filenames[0])


def main():
    parser = argparse.ArgumentParser(
        description="Utility resolve a robotics URI ({}) to an absolute filename.".format(
            ", ".join(f"{scheme}://" for scheme in SupportedSchemes)
        )
    )
    parser.add_argument("uri", metavar="URI", type=str, help="URI to resolve")

    args = parser.parse_args()

    try:
        result = resolve_robotics_uri(args.uri)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print(result, file=sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
