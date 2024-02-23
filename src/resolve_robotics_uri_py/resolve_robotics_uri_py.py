import argparse
import os
import pathlib
import sys
from typing import List
import warnings

# Function inspired from https://github.com/ami-iit/robot-log-visualizer/pull/51
def get_search_paths_from_envs(env_list):
    return [
        pathlib.Path(f) if (env != "AMENT_PREFIX_PATH") else pathlib.Path(f) / "share"
        for env in env_list if os.getenv(env) is not None
        for f in os.getenv(env).split(os.pathsep)
    ]

def pathlist_list_to_string(path_list):
    return ' '.join(str(path) for path in path_list)

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
    env_list = ["GAZEBO_MODEL_PATH", "ROS_PACKAGE_PATH", "AMENT_PREFIX_PATH", "SDF_PATH", "IGN_GAZEBO_RESOURCE_PATH", "GZ_SIM_RESOURCE_PATH"]

    # Preliminary step: if there is no scheme, we just consider this a path and we return it as it is
    if "://" not in uri:
        return pathlib.Path(uri)

    # Get scheme from URI
    from urllib.parse import urlparse
    parsed_uri = urlparse(uri)

    # We only support the following URI schemes at the moment:
    #
    # * file://:    to pass an absolute file path directly
    # * model://:   SDF-style model URI
    # * package://: ROS-style package URI
    #
    if parsed_uri.scheme not in {"file", "package", "model"}:
        raise FileNotFoundError(f"Passed URI \"{uri}\" use non-supported scheme {parsed_uri.scheme}")

    model_filenames = []

    if parsed_uri.scheme == "file":
        model_filenames.append(uri.replace("file:/", ""))

    if parsed_uri.scheme == "package" or parsed_uri.scheme == "model":
        uri_path = uri.replace(f"{parsed_uri.scheme}://","")
        for folder in get_search_paths_from_envs(env_list):
            candidate_file_name = folder / pathlib.Path(uri_path)
            if (candidate_file_name.is_file()):
                if candidate_file_name not in model_filenames:
                    model_filenames.append(candidate_file_name)

    if model_filenames:
        if (len(model_filenames) > 1):
            warnings.warn(f"resolve-robotics-uri-py: Multiple files ({pathlist_list_to_string(model_filenames)}) found for uri \"{uri}\", returning the first one.")
        return pathlib.Path(model_filenames[0])

    # If no file was found raise error
    raise FileNotFoundError(f"resolve-robotics-uri-py: No file corresponding to uri \"{uri}\" found")

def main():
    parser = argparse.ArgumentParser(description="Utility resolve a robotics URI (file://, model://, package://) to an absolute filename.")
    parser.add_argument("uri", metavar="uri", type=str, help="URI to resolve")

    args = parser.parse_args()
    result = resolve_robotics_uri(args.uri)

    print(result)
    sys.exit(0)

if __name__ == "__main__":
    main()
