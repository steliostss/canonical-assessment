"""
	File name: package_statistics.py
	Author: Tsagkarakis Stelios
	Date created: 16/11/2022
	Python version: 3

	Description: python command line tool that takes the architecture
		     (amd64, arm64, mips etc.) as an argument and downloads
		     the compressed Contents file associated with it from a
		     Debian mirror. The program should parse the file and
		     output the statistics of the top 10 packages that have
		     the most files associated with them.
       
    Exit codes:
         0: Execution completed succesfully
        -1: Could not download file
        -2: Could not delete file after execution completed
"""

from __future__ import annotations
from typing import List  # type hinting

from urllib.error import URLError
import urllib.request
import argparse
import os
import gzip
import re


def parse_arguments(filename: str, archs: List[str]) -> argparse.Namespace:
    """Parse the command line arguments. Exits if required arguments conditions are not met.

    Args:
        filename (str): Name of currently executed file
        archs List[str]: List of accepted architectures

    Returns:
        argparse.Namespace: Namespace with the list of arguments
    """

    argparser = argparse.ArgumentParser(
        usage="python3 " + filename + " <arch>",
        description="python command line tool that takes the architecture\
                    (amd64, arm64, mips etc.) as an argument and downloads\
                    the compressed Contents file associated with it from a\
                    Debian mirror. The program outputs the top 10 packages\
                    that have the most files associated with them."
    )

    # pop the "optional" group to add required group only
    argparser._action_groups.pop()
    # argparser._action_groups.append(optional)
    required = argparser.add_argument_group("required arguments")

    # join the architectures in a comma separated string
    help_msg = ', '.join(map(str, archs))
    help_msg = "--> Accepted architectures: " + help_msg
    required.add_argument("arch", nargs=1, default="",
                          type=str, help=help_msg)

    args = argparser.parse_args()
    return args


def clean_package_str(line: str) -> List[str]:
    """Strip spaces and seperate file and packages for the input line.

    Args:
        line (str): Input line from the target architecture Contents-$ARCH.gz file

    Returns:
        List[str]: List of 2. L[0] is the file, L[1] is(are) the corresponding package(s)
    """

    # replace consecutive spaces with a single space
    result = re.sub(' +', ' ', line.strip())
    result = result.strip().split(' ')  # split by the remaining space
    return ['', '']


def initiate_execution(arch: str) -> None:
    """ Start main execution. Read architecture and download the "Contents-$arch.gz" file.
    After finalising execution delete the downloaded file.

    Args:
        arch (str): Target architecture

    Raises:
        URLError: If download could not be completed from the specified URL    
        OSError: If downloaded file could not be deleted
    """

    uri = "http://ftp.uk.debian.org/debian/dists/stable/main/"
    contents = "Contents-"+arch+".gz"
    print("Downloading file...")
    try:
        # download file from mirror link
        urllib.request.urlretrieve(uri+contents, contents)
        f = gzip.open(contents, mode='rt')  # read compressed file in text mode
        Lines = f.readlines()  # read by lines

        # count = 0
        # for line in Lines:
        #     count += 1
        #     print(result)
        #     if (count == 5):
        #         break
        # attempt to delete file, check for OSError
        try:
            os.remove(contents)
            print("File deleted.")
        except OSError:
            print("Could not delete file: " + contents)
            exit(-2)
    except URLError as e:
        print("Could not find file to download.")
        print("Check internet connection or specify the correct url.")
        exit(-1)


if __name__ == "__main__":
    accepted_architectures = ["i386", "amd64", "armel", "arm64",
                              "armhf", "mips", "mipsel", "mips64el", "ppc64el", "s390x"]
    filename: str = __file__.split('/')[-1]
    args = parse_arguments(filename, accepted_architectures)

    try:
        # assert (args.arch) # this scenario is handled by argparser
        # validate architecture
        assert (args.arch[0] in accepted_architectures)
        print(*args.arch)
        initiate_execution(args.arch[0])
    except AssertionError:
        # print explanatory message
        print(
            "Error! Specify the correct required command line argument for the target architecture.\n")
        print("Accepted architectures:\n\t", end='')
        print(*accepted_architectures, sep=', ', end='\n\n')
        print("For help, run:")
        print("\t" + filename + " --help")
