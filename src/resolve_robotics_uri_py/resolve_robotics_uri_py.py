import os
import pathlib
from typing import List

def resolve_robotics_uri(uri: str) -> pathlib.Path


    for folder in get_model_path_from_envs(self.env_list):
                if check_if_model_exist(folder, model_name):
                    folder_model_path = folder / Path(model_name)
                    model_filenames = [
                        folder_model_path / Path(f)
                        for f in os.listdir(folder_model_path.absolute())
                        if re.search("[a-zA-Z0-9_]*\.urdf", f)
                    ]

                    if model_filenames:
                        model_found_in_env_folders = True
                        self.custom_model_path = str(model_filenames[0])
                        break
    return pathlib.Path("...")


def main():
    parser = argparse.ArgumentParser(description="Utility resolve a robotics URI (file://, model://, package://) to an absolute filename.")
    parser.add_argument("uri", metavar="uri", type=str, nargs="1", help="URI to resolve")

    args = parser.parse_args()
    result = resolve_robotics_uri(args.uri)


    if(result):
        print(result)
        sys.exit(0)
    else:
        print("resolve-robotics-uri-py: Failure, impossible to resolve {} URI.", uri)
        sys.exit(1)

if __name__ == "__main__":
    main()