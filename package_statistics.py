"""
    Python script that takes the architecture (amd64, arm64, mips etc.)
    as an argument and downloads the compressed Contents file associated
    with it from a Debian mirror. The program parses the file and outputs
    the names of the top 10 packages that have the most files associated
    with them.
"""

from __future__ import annotations

import urllib.request
import argparse
import os
import gzip
import re
import sys
import heapq
import tempfile

from typing import List, Union, Dict  # type hinting
from urllib.error import URLError


def parse_arguments(fname: str, archs: List[str]) -> argparse.Namespace:
    """Parse the command line arguments. Exits if required arguments conditions are not met.

    Args:
        filename (str): Name of currently executed file
        archs List[str]: List of accepted architectures

    Returns:
        argparse.Namespace: Namespace with the list of arguments
    """

    argparser = argparse.ArgumentParser(
        usage="python3 " + fname + " <arch>",
        description=__doc__
    )

    # pop the "optional" group to add required group only
    # optional = argparser._action_groups.pop()
    # argparser._action_groups.append(optional)
    # required = argparser.add_argument_group("required arguments")
    # optional = argparser.add_argument_group("optional arguments")

    # join the architectures in a comma separated string
    help_msg = ', '.join(map(str, archs))
    help_msg = "Accepted architectures: " + help_msg
    argparser.add_argument("arch", nargs=1, default="",
                           type=str, help=help_msg)

    argparser.add_argument("-n", default=10, type=int, nargs=1,
                           help="Get the top-N packages. Default 10.")

    arguments = argparser.parse_args()
    return arguments


def clean_package_str(line: str) -> List[Union[str, List[str]]]:
    """Strip spaces and seperate file and packages for the input line.

    Args:
        line (str): Input line from the target architecture Contents-$ARCH.gz file

    Returns:
        List[str | List[str]]: List of 2 elements. L[0] is the file
        and L[1] is a list of the required corresponding packages
    """

    # replace consecutive spaces with a single space
    dep_line = re.sub(' +', ' ', line.strip())
    separated_line = dep_line.strip().split(' ')  # split by the remaining space
    ref_file = separated_line[0]  # define reference file

    if len(separated_line) == 1:
        packages = [""]  # if there are no required packages add an empty list
    else:
        # else add the required packages list
        packages = separated_line[1].split(',')

    # result[1] = result[1].split(',')
    return [ref_file, packages]


def get_file(arch: str, temp_dir: str) -> str:
    """Get the target architecture and download the corresponding
    "Contents-$arch.gz" file for a debian mirror.

    Args:
        arch (str): Target architecture
        temp_dir (str): Temporary Directory to save file

    Returns:
        str: Name of downloaded file
    """

    uri = "http://ftp.uk.debian.org/debian/dists/stable/main/"
    contents = "Contents-" + arch + ".gz"
    full_path = os.path.join(temp_dir, contents)

    # download file from mirror link
    urllib.request.urlretrieve(uri+contents, full_path)

    return full_path


def count_package_occurence(package_file_list: List[Union[str, List[str]]],
                            package_dict: Dict[str, int]) -> None:
    """Count the occurences of each package and increment a counter in the corresponding
    entry of a given dictionary.

    Args:
        package_file_list (List[Union[str, List[str]]]): Two element list,
        L[0] is the file and L[1] is a List of the required packages
        package_dict (Dict[str, int]): Stores (key:value) pairs as (package_name:occurences)
    """

    for pkg in package_file_list[1]:
        # add an occurence if it does not exist or just increment by 1
        package_dict[pkg] = package_dict[pkg] + \
            1 if (pkg in package_dict) else 1


def get_occurences_dictionary(arguments: argparse.Namespace) -> Dict[str, int]:
    """Start main execution. Read architecture and download the "Contents-$arch.gz" file.
    After finalising execution delete the downloaded file.

    Args:
        args (argparse.Namespace): Command line arguments

    Returns:
        Dict[str, int]: Returns (key:value) pairs as (package_name:occurences)

    Raises:
        URLError: If download could not be completed from the specified URL
        OSError: If downloaded file could not be deleted
    """

    try:
        package_dict = {}
        # open a temporary directory download file
        with tempfile.TemporaryDirectory() as tempdirname:
            contents = get_file(arguments.arch[0], tempdirname)
            # read compressed file in text mode
            contents_file = gzip.open(contents, mode='rt')
            contents_lines = contents_file.readlines()  # read by lines
            # count = 0
            for line in contents_lines:
                # get the two element list from the line: [file, packages]
                package_file_list = clean_package_str(line)

                # count the occurence of each package in the package list
                count_package_occurence(package_file_list, package_dict)

            # finally close the file
            contents_file.close()
            # file is deleted upon exit

        return package_dict  # finally return

    except URLError as caught_error:
        print(caught_error.reason)
        print("Check internet connection or specify the correct url.")
        sys.exit(-1)


def get_top_n_elements(package_dict: Dict[str, int], top_n: int) -> List[str]:
    """Return a list of the top "top_n" elements with most occurences

    Args:
        package_dict (Dict[str, int]): (key:value) pairs as (package_name:occurences)
        n (int): Top n elements

    Returns:
        List[str]: A list with the top n elements (without the occurence)
    """

    # get the N most frequent packages using heapq which is of O(N) complexity
    top_n_packages = heapq.nlargest(
        top_n, package_dict, key=lambda key: package_dict[key])

    return top_n_packages


def print_formatted(package_dict: Dict[str, int], top_n: List[str]) -> None:
    """Print the top N elements of "dict" formatted in two columns

    Args:
        package_dict (Dict[str,int]): (key:value) pairs as (package_name:occurences)
        top_n (List[str]): the top N elements
    """

    for idx, item in enumerate(top_n):
        print(f'{idx+1:>4}' + ". " + f'{item:<50}' +
              "\t", package_dict[item], sep='')


if __name__ == "__main__":
    accepted_architectures = ["i386", "amd64", "armel", "arm64",
                              "armhf", "mips", "mipsel", "mips64el", "ppc64el", "s390x"]
    filename: str = __file__.rsplit('/', maxsplit=1)[-1]
    args = parse_arguments(filename, accepted_architectures)

    try:
        # assert (args.arch) # this scenario is handled by argparser
        # validate architecture
        assert args.arch[0] in accepted_architectures

        # get the dictionary with packages occurences counted
        res_dict = get_occurences_dictionary(args)
        # retrieve the top n
        max_packages = get_top_n_elements(res_dict, args.n)
        print_formatted(res_dict, max_packages)  # print the values formatted

    except AssertionError:
        # print explanatory message
        print(
            "Error! Specify the correct target architecture.\n")
        print("Accepted architectures:\n\t", end='')
        print(*accepted_architectures, sep=', ', end='\n\n')
        print("For help, run:")
        print("\t" + filename + " --help")
