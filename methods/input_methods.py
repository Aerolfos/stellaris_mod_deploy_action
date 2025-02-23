import argparse
import os
import re
import subprocess
from pathlib import Path


def str2bool(v: str) -> bool:
    """
    Parses a string value for a true-like or false-like value to be turned into a `bool`

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
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        msg = "Boolean value expected."
        raise argparse.ArgumentTypeError(msg)


def get_env_variable(env_var_name: str, default: str | None = None, debug_level: int = 1) -> str:
    """Simple getenv wrapper with debug print"""
    env_var = os.getenv(env_var_name, default)
    if debug_level in ["INFO", "DEBUG"]:
        print(f"{env_var_name}={env_var}")
    return env_var


def parse_descriptor_to_dict(descriptor_file_path: Path, debug_level: int = 0) -> dict:
    """
    Creates a dict of entries from a paradox descriptor.mod file

    This method relies on the fixed structure of .mod files set by paradox
    Stellaris and its mod upload tools are more restrictive than this parser, be wary of that.
    Specifically, this parser has extensions to allow for use with overrides,
    like supporting {} blocks for later formatting in Python

    Parser will skip empty lines and comments, indicated with #. This includes empty lines in multi-line blocks.'
    In-line comments are NOT supported.
    """
    if debug_level == "DEBUG":
        print("- Parsing descriptor style file -")
        print(f"Path: {descriptor_file_path}")
    descriptor_dict = {}
    line_container = []
    multiline_flag = False
    with Path.open(descriptor_file_path, encoding="utf-8") as descriptor_object:
        for line in descriptor_object:
            # debug prints
            if debug_level == "DEBUG":
                print()  # implicit newline
                if multiline_flag:
                    print("Multiline parsing enabled")
                print(f"Current line: {line.rstrip('\n')}")

            # skip empty lines and # comments
            if not line or line.isspace():
                if debug_level == "DEBUG":
                    print("Skipping blank line")
                continue
            # strip any spaces or tabs before any comment
            # the simple descriptor format does NOT support inline comments, hence ignoring # not at beginning
            if line.lstrip().startswith("#"):
                if debug_level == "DEBUG":
                    print("Line is comment, skipping")
                continue
            # check for normal parsing
            if not multiline_flag:
                if "=" in line:
                    # strip line for trailing spaces and turn line into list with key and value
                    line = line.rstrip().split("=")
                    line[0] = line[0].strip()
                    line[1] = line[1].strip().strip('"')

                    if debug_level == "DEBUG":
                        print(f"Split line list: {line}")

                    if not line[1].lstrip().startswith("{"):
                        descriptor_dict[line[0]] = line[1]

                        if debug_level == "DEBUG":
                            print("Saving line:")
                            print(f"'{line[0]}' : '{line[1]}'")

                    # the multiline blocks like tags are a problem, so parse those
                    elif line[1].lstrip().startswith("{"):
                        if "}" not in line[1]:
                            if debug_level == "DEBUG":
                                print("Started multiline")

                            multiline_key = line[0]
                            multiline_flag = True
                            # check for anything after the brace - you shouldn't do this but you never know...
                            index_brace = line[1].find("{")
                            if not (line[1].endswith("{") or line[1].endswith(" ")):
                                # save anything after the brace unless the brace is last character (string was stripped already)
                                extra_item = line[1][index_brace + 1 :].lstrip('"')
                                line_container.append(extra_item)

                                if debug_level == "DEBUG":
                                    print(f"Found item after '{{', was: '{extra_item}'")
                            continue  #  goes to next line
                        else:
                            # line is like
                            # tags = { "tag1" "tag2" "tag3" "tag4" "tag5"}
                            if debug_level == "DEBUG":
                                print("Single line listlike")

                            multiline_key = line[0]
                            index_lbrace = line[1].find("{")
                            index_rbrace = line[1].find("}")
                            contents = line[1][index_lbrace + 1 : index_rbrace].strip()
                            line_container = contents.split('" "')
                            line_container = [word.strip('"') for word in line_container]

                            if debug_level == "DEBUG":
                                print("Contents:", line_container)

                            descriptor_dict[multiline_key] = line_container
                            if debug_level == "DEBUG":
                                print("Saving line:")
                                print(f"'{multiline_key}' : '{line_container}'")

                            # clear list of saved tags
                            line_container = []

            # alternate flow
            elif multiline_flag:
                if "}" not in line:
                    line_item = line.strip().strip('"')
                    line_container.append(line_item)

                    if debug_level == "DEBUG":
                        print(f"Found item: '{line_item}'")

                if "}" in line:
                    if debug_level == "DEBUG":
                        print("Last line in multiline found")

                    line = line.lstrip().strip('"')
                    # check for anything before the brace - you shouldn't do this but you never know...
                    index_brace = line.find("}")
                    if not line.startswith(("}", " ")):
                        # save anything before the brace unless it's last character
                        # make sure the quote markers are gone from item
                        extra_item = line[:index_brace].rstrip('"')
                        if debug_level == "DEBUG":
                            print(f"Found item after '}}', was: '{extra_item}'")

                        line_container.append(extra_item)

                    # end multiline
                    descriptor_dict[multiline_key] = line_container
                    if debug_level == "DEBUG":
                        print("Saving line:")
                        print(f"'{multiline_key}' : '{line_container}'")

                    # clean up
                    multiline_flag = False
                    line_container = []
                    continue  # keep parsing next line

    if debug_level == "DEBUG":
        print("Finished parsing")
        print(f"result = {descriptor_dict}")

    return descriptor_dict


def create_descriptor_file(descriptor_dict: dict, descriptor_file_path: Path) -> None:
    """Creates a paradox descriptor.mod file from a dictionary"""
    with Path.open(descriptor_file_path, "w", encoding="utf-8") as descriptor_object:
        # dict order being insertion order is guaranteed in newer python versions so file structure should be preserved
        for key, item in descriptor_dict.items():
            # construct line - in case of list we need to write it out tabbed and encased in {}
            if isinstance(item, str):
                line = f'{key}="{item}"\n'
                descriptor_object.write(line)
            elif isinstance(item, list):
                line = f"{key}={{\n"
                descriptor_object.write(line)
                for tag in item:
                    # \t for tab
                    line = f'\t"{tag}"\n'
                    descriptor_object.write(line)
                # end block and continue other items
                descriptor_object.write("}\n")
    print(f"File {descriptor_file_path} written")


def mod_version_to_dict(
    input_mod_version: str,
    *,
    use_format_check: bool = True,
    possible_version_types: list = ("Major", "Minor", "Patch"),
    regex_version_pattern: str | None = None,
) -> tuple[dict, bool, bool]:
    """
    Take a string with a version of the form "v1.2.3" and return a dict with the version components

    Uses a regex pattern to make sure the format is correct - can be optionally skipped
    Has a default pattern but can be overriden

    Possible versions list must be in the same order as the version is structured
    """
    using_v_prefix = False
    using_v_with_space_prefix = False

    if use_format_check:
        if regex_version_pattern is None:
            # matches format "1.2.3" or alternatively "v1.2.3", * wildcards allowed
            regex_version_pattern = r"^v?\s?(?:(?:\d{1,9}|\*)\.){2}(?:\d{1,9}|\*)"  # yeah regex be like that

        if not re.search(regex_version_pattern, input_mod_version, re.IGNORECASE):
            if re.search(r"\d{10}", input_mod_version, re.IGNORECASE):
                msg = "Maximum number of digits (9) for a version number was exceeded. Why have you done this?"
                raise ValueError(msg)
            msg = f'Version format should be of type "v1.2.3", got "{input_mod_version}"'
            raise ValueError(msg)

    semantic_version_list = input_mod_version.split(".")
    # save the v and potential space for later
    if semantic_version_list[0].startswith("v"):
        semantic_version_list[0] = semantic_version_list[0].lstrip("v")
        using_v_prefix = True
        if semantic_version_list[0].startswith(" "):
            semantic_version_list[0] = semantic_version_list[0].lstrip(" ")
            using_v_with_space_prefix = True

    current_semantic_versions = dict(zip(possible_version_types, semantic_version_list, strict=True))

    return current_semantic_versions, using_v_prefix, using_v_with_space_prefix


def increment_mod_version(
    input_mod_version: str,
    patch_type: str,
    *,
    use_format_check: bool = True,
    possible_version_types: list = ("Major", "Minor", "Patch"),
    regex_version_pattern: str | None = None,
) -> tuple[dict, str]:
    """
    Take a version of the form "v1.2.3" and increment according to patch type

    Uses a regex pattern to make sure the format is correct - can be optionally skipped

    Possible versions list must be in the same order as the version is structured
    """
    # break down with helper function
    current_semantic_versions, using_v_prefix, using_v_with_space_prefix = mod_version_to_dict(
        input_mod_version,
        use_format_check=use_format_check,
        possible_version_types=possible_version_types,
        regex_version_pattern=regex_version_pattern,
    )

    # check what versions follow from the currently selected version by slicing
    subsequent_versions = possible_version_types[possible_version_types.index(patch_type) + 1 :]
    # these should be zeroed if we're updating a higher version
    # if there's no extra versions nothing happens
    for version_to_zero in subsequent_versions:
        if "*" not in current_semantic_versions[version_to_zero]:
            current_semantic_versions[version_to_zero] = "0"

    # increment, but ignore asterisks
    if "*" not in current_semantic_versions[patch_type]:
        current_semantic_versions[patch_type] = str(int(current_semantic_versions[patch_type]) + 1)

    # NOTE: stellaris prefers v1.2.3 now
    updated_mod_version = ".".join(current_semantic_versions.values())
    if using_v_prefix:
        if using_v_with_space_prefix:
            updated_mod_version = " " + updated_mod_version
        updated_mod_version = "v" + updated_mod_version
    return current_semantic_versions, updated_mod_version


def search_and_replace_in_file(
    file_path: Path,
    pattern: str | list,
    replacestr: str | list,
    *,
    return_old_str: bool = False,
) -> str | tuple[str, str]:
    """
    Opens a file and replaces a part of it via regex

    Use to update version number and similar in text descriptions

    Can take in one pattern, or a list of them to go through and match

    Returns the new file string in case info from file is useful - option to also get old string
    """
    # read into holder string for searching
    file_handle = Path.open(file_path)
    file_string = file_handle.read()
    file_handle.close()
    original_file_string = file_string

    if isinstance(pattern, list):
        if isinstance(replacestr, list):
            for selected_pattern, selected_replacementstr in zip(pattern, replacestr, strict=False):
                file_string = re.sub(
                    selected_pattern,
                    selected_replacementstr,
                    file_string,
                    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                )
        else:
            # reuse the same pattern multiple times
            for selected_pattern in pattern:
                file_string = re.sub(selected_pattern, replacestr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    elif isinstance(pattern, str):
        if isinstance(replacestr, str):
            file_string = re.sub(pattern, replacestr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        else:
            msg = "Passed only one pattern but multiple replacement strings, types must match"
            raise TypeError(msg)
    else:
        msg = f"Input search pattern must be a single str or a list of str, got {type(pattern)}"
        raise TypeError(msg)

    # w overwrites file
    file_handle = Path.open(file_path, "w")
    file_handle.write(file_string)
    file_handle.close()

    if return_old_str:
        return original_file_string, file_string
    else:
        return file_string


def generate_with_template_file(
    template_file_path: Path,
    generated_file_path: Path,
    pattern: str | list,
    replacestr: str | list,
    *,
    skip_regex_replace: bool = False,
) -> str:
    """
    Uses a template file to generate a new file with part of it replaced via regex

    Useful for filling in changelog to a release note template

    Can take in one pattern, or a list of them to go through and match

    If skip is enabled, skips the regex search - just pass empty strings for pattern and replacestr

    Returns the file string in case info from file is useful
    """
    # read template into holder string
    file_handle = Path.open(template_file_path)
    file_string = file_handle.read()
    file_handle.close()

    if skip_regex_replace is False:
        # fill in to template via regex search
        if isinstance(pattern, list):
            if isinstance(replacestr, list):
                for selected_pattern, selected_replacementstr in zip(pattern, replacestr, strict=False):
                    file_string = re.sub(
                        selected_pattern,
                        selected_replacementstr,
                        file_string,
                        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                    )
            else:
                # reuse the same pattern multiple times
                for selected_pattern in pattern:
                    file_string = re.sub(
                        selected_pattern,
                        replacestr,
                        file_string,
                        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                    )
        elif isinstance(pattern, str):
            if isinstance(replacestr, str):
                file_string = re.sub(pattern, replacestr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
            else:
                msg = "Passed only one pattern but multiple replacement strings, types must match"
                raise TypeError(msg)
        else:
            msg = f"Input search pattern must be a single str or a list of str, got {type(pattern)}"
            raise TypeError(msg)

    # w writes new file
    file_handle = Path.open(generated_file_path, "w")
    file_handle.write(file_string)
    file_handle.close()

    return file_string
