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
    
def parse_descriptor_to_dict(descriptor_file_object: Path) -> dict:
    """Creates a dict of entries from a paradox descriptor.mod file
    
    This method relies on the fixed structure of pdx script, {} are indicators for blocks that go together.

    Doing something like putting "}" in your version will break this script, but it will also break Stellaris and its mod upload tools, so, maybe don't do that.
    """
    descriptor_dict = {}
    line_container = []
    multiline_flag = False
    with open(descriptor_file_object, 'r', encoding="utf-8") as descriptor:
        for line in descriptor:
            if not multiline_flag:    
                if "=" in line:
                    # strip line for trailing spaces and turn line into list with key and value
                    line = line.rstrip().split("=")
                    line[1] = line[1].strip("\"")
                    # the multiline blocks like tags are a problem, so parse those
                    if "{" in line[1]:
                        multiline_key = line[0]
                        multiline_flag = True
                        # check for anything after the brace - you shouldn't do this but you never know...
                        index_brace = line[1].find("{")
                        if not (line[1].endswith("{") or line[1].endswith(" ")):
                            # save anything after the brace unless it's last character (string was stripped already)
                            line_container.append(line[1][index_brace+1:])
                        continue #  goes to next line
                    else:
                        descriptor_dict[line[0]] = line[1]
            elif multiline_flag:
                if "}" in line:
                    descriptor_dict[multiline_key] = line_container
                    multiline_flag = False
                    line_container = [] # clean up container
                    continue #  goes to next line
                else:
                    line_container.append(line.strip().strip("\""))
    return descriptor_dict

def increment_mod_version(
        input_mod_version: str, 
        patch_type: str, 
        use_format_check: bool = True, 
        possible_version_types: list = ["Major", "Minor", "Patch"]
    ) -> tuple[dict, str]:
    """Take a version of the form "1.2.3" and increment according to patch type

    Uses a regex pattern to make sure the format is correct - can be optionally skipped

    Possible versions list must be in the same order as the version is structured
    """
    if use_format_check:
        # matches format "1.2.3" or alternatively "v1.2.3", * wildcards allowed
        regex_version_pattern = r"^v?\s?(?:(?:\d{1,3}|\*)\.){2}(?:\d{1,3}|\*)" # yeah regex be like that
        if not re.search(regex_version_pattern, input_mod_version, re.IGNORECASE):
            raise ValueError(f"Version format should be of type \"1.2.3\", got {input_mod_version}")

    semantic_version_list = input_mod_version.split(".")
    # save the v and potential space for later
    if semantic_version_list[0].startswith("v"):
        semantic_version_list[0] = semantic_version_list[0].lstrip("v")
        using_v_prefix = True
        if semantic_version_list[0].startswith(" "):
            semantic_version_list[0] = semantic_version_list[0].lstrip(" ")
            using_v_with_space_prefix = True

    current_semantic_versions = dict(zip(possible_version_types, semantic_version_list))

    # check what versions follow from the currently selected version by slicing
    subsequent_versions = possible_version_types[possible_version_types.index(patch_type)+1:]
    # these should be zeroed if we're updating a higher version
    # if there's no extra versions nothing happens
    for version_to_zero in subsequent_versions:
        if "*" not in current_semantic_versions[version_to_zero]:
            current_semantic_versions[version_to_zero] = "0"
    
    # increment, but ignore asterisks
    if "*" not in current_semantic_versions[patch_type]:
        current_semantic_versions[patch_type] = str(int(current_semantic_versions[patch_type]) + 1)
    
    updated_mod_version = ".".join(current_semantic_versions.values())
    if using_v_prefix:
        if using_v_with_space_prefix:
            updated_mod_version = " " + updated_mod_version
        updated_mod_version = "v" + updated_mod_version
    return current_semantic_versions, updated_mod_version
