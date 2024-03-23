import argparse
import re
from pathlib import Path

def str2bool(v: str) -> bool:
    """Parses a string value for a true-like or false-like value to be turned into a `bool`

    Meant to be used with `argparse` for command line inputs. Raises appropriate error to parser.

    Parameters
    ----------
    v : str
        Input should be a bool-like string.

        Something like "yes", "true", "1", for True, or "no", "false", "0" for False.

    Returns
    -------
    v : bool
        Output value is a Python `bool`, strictly `True` or `False`.

    Raises
    ------
    argparse.ArgumentTypeError
        Could not convert value supplied. 
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# this is really simple boilerplate, wrapped in functions for less code repetition
def extract_file_data(file: Path) -> str:
    """Read contents from file into memory as a single string
    
    Closes file immediately to avoid interference.
    """
    file_handle = open(file, 'r', encoding="utf-8")
    file_string = file_handle.read()
    file_handle.close()

    return file_string

def replace_file_data(file: Path, file_string: str) -> None:
    """Write str data to file, replacing it
    
    Closes file immediately to avoid interference.
    """
    file_handle = open(file, 'w', encoding="utf-8")
    file_handle.write(file_string)
    file_handle.close()

    return None

# actual methods
def extract_and_replace_mod_version(file_string: str, pattern: str, patch_type: str) -> str:
    """Finds a version number from a paradox descriptor file, and increments it
    
    Uses regular expressions, regex pattern must create a group for the version number
    """
    if match := re.search(pattern, file_string, re.IGNORECASE):
        extracted_mod_version = match.group(1)

    updated_mod_version = increment_mod_version(extracted_mod_version, patch_type)

    # use re package to allow for regex replacement
    file_string = (re.sub(pattern, subst, file_string))

    return updated_mod_version

def increment_mod_version(input_mod_version: str, patch_type: str) -> str:
    """Take a version of the form "1.2.3" and increment according to patch type
    """
    return updated_mod_version
