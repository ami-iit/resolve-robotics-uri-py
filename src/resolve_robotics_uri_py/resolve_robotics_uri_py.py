import os
import pathlib
from typing import List

def resolve_robotics_uri(uri: str) -> pathlib.Path


    # 
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