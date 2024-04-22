import argparse
import re
from pathlib import Path
from typing import Union

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
    
    Parses will skip empty lines and comments, indicated with #. This includes empty lines in multi-line blocks.
    """
    descriptor_dict = {}
    line_container = []
    multiline_flag = False
    with open(descriptor_file_object, 'r', encoding="utf-8") as descriptor:
        for line in descriptor:
            # skip empty lines and # comments
            if not line or line.isspace():
                continue
            # strip any spaces or tabs before the comment
            if line.lstrip().startswith("#"):
                continue
            # check for normal parsing
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
            # alternate flow
            elif multiline_flag:
                if "}" in line:
                    descriptor_dict[multiline_key] = line_container
                    multiline_flag = False
                    line_container = [] # clean up container
                    continue #  goes to next line
                else:
                    line_container.append(line.strip().strip("\""))
    return descriptor_dict

def create_descriptor_file(descriptor_dict: dict, descriptor_file_object: Path) -> None:
    """Creates a paradox descriptor.mod file from a dictionary
    """
    with open(descriptor_file_object, 'w', encoding="utf-8") as descriptor:
        # dict order being insertion order is guaranteed in newer python versions so file structure should be preserved
        for key, item in descriptor_dict.items():
            # construct line - in case of list we need to write it out tabbed and encased in {}
            if isinstance(item, str):
                line = f"{key}=\"{item}\"\n"
                descriptor.write(line)
            elif isinstance(item, list):
                line = f"{key}={{\n"
                descriptor.write(line)
                for tag in item:
                    # \t for tab
                    line = f"\t\"{tag}\"\n"
                    descriptor.write(line)
                # end block and continue other items
                descriptor.write(f"}}\n")
    print(f"File {descriptor_file_object} written")

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
    using_v_prefix = False
    using_v_with_space_prefix = False

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

def search_and_replace_in_file(file_path: Path, pattern: Union[str, list], substr: str, return_old_str: bool = False) -> Union[str, tuple[str, str]]:
    """Opens a file and replaces a part of it via regex

    Use to update version number and similar in text descriptions

    Can take in one pattern, or a list of them to go through and match

    Returns the new file string in case info from file is useful - option to also get old string
    """
    # read into holder string for searching
    file_handle = open(file_path, 'r')
    file_string = file_handle.read()
    file_handle.close()
    original_file_string = file_string

    if isinstance(pattern, list):
        for selected_pattern in pattern:
            file_string = re.sub(selected_pattern, substr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    elif isinstance(pattern, str):
        file_string = re.sub(pattern, substr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    else:
        raise TypeError(f"Input search pattern must be a single str or a list of str, got {type(pattern)}")

    # w overwrites file
    file_handle = open(file_path, 'w')
    file_handle.write(file_string)
    file_handle.close()

    if return_old_str:
        return original_file_string, file_string
    else:
        return file_string

def generate_with_template_file(template_file_path: Path, generated_file_path: Path, pattern: Union[str, list], substr: str) -> str:
    """Uses a template file to generate a new file with part of it replaced via regex

    Useful for filling in changelog to a release note template

    Can take in one pattern, or a list of them to go through and match

    Returns the file string in case info from file is useful
    """
    # read template into holder string
    file_handle = open(template_file_path, 'r')
    file_string = file_handle.read()
    file_handle.close()

    # fill in to template via regex search
    if isinstance(pattern, list):
        for selected_pattern in pattern:
            file_string = re.sub(selected_pattern, substr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    elif isinstance(pattern, str):
        file_string = re.sub(pattern, substr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    else:
        raise TypeError(f"Input search pattern must be a single str or a list of str, got {type(pattern)}")

    # w writes new file
    file_handle = open(generated_file_path, 'w')
    file_handle.write(file_string)
    file_handle.close()

    return file_string

