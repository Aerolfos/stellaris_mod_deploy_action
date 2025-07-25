"""Functions for handling various user input"""

import argparse
import os
import re
import zipfile
from pathlib import Path


def str2bool(v: str | None) -> bool:
    """
    Parses a string value for a true-like or false-like value to be turned into a `bool`

    Meant to be used with `argparse` for command line inputs. Raises appropriate error to parser.

    Parameters
    ----------
    v : str | None
        Input should be a bool-like string.

        Something like "yes", "true", "1", for True, or "no", "false", "0" for False.

        Technically `None` is also accepted, as usual in Python `None` is falsy.

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
    if v is None:
        return False
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        msg = "Boolean value expected."
        raise argparse.ArgumentTypeError(msg)


def get_env_variable(env_var_name: str, default: str | None = None, debug_level: str = "INFO") -> str | None:
    """Simple getenv wrapper with debug print"""
    env_var = os.getenv(env_var_name, default)
    if debug_level in ["INFO", "DEBUG"]:
        print(f"{env_var_name}={env_var}")
    return env_var


def parse_descriptor_to_dict(descriptor_file_path: Path, debug_level: str = "SILENT") -> dict[str, str]:
    """
    Creates a dict of entries from a paradox descriptor.mod file

    This method relies on the fixed structure of .mod files set by paradox
    Stellaris and its mod upload tools are more restrictive than this parser, be wary of that.
    Specifically, this parser has extensions to allow for use with overrides,
    like supporting {} blocks for later formatting in Python

    Parser will skip empty lines and comments, indicated with #. This includes empty lines in multi-line blocks.'
    In-line comments are NOT supported (Stellaris does not support this either).

    Parameters
    ----------
    descriptor_file_path : Path
        Input `pathlib.Path` object pointing to a `descriptor.mod` style file, which will be parsed

    debug_level : str
        One of "SILENT", "INFO", or "DEBUG", for enabling print statements during parsing

    Returns
    -------
    descriptor_dict : dict[str: str]
        A Python-appropriate representation of the key-value content that was in the descriptor file.
        See tests for examples, like `expected_test_descriptor_dict` in `conftest.py`.

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
    """
    Creates a paradox `descriptor.mod` file from a dictionary

    Very simplistic and rigid file writing, on purpose. Paradox tools are very particular about reading descriptors.
    """
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
    possible_version_types: list[str] | tuple = ("Major", "Minor", "Patch"),
    regex_version_pattern: str | None = None,
) -> tuple[dict, bool, bool]:
    """
    Take a string with a version of the form `(v)1.2.3` and return a dict with the version components

    Uses a regex pattern to make sure input version format is correct - this can optionally be skipped.
    Supplied with a default pattern looking for `(v)1.2.3`, can be supplied a different regex pattern.
    Default pattern allows for up to 9 digits per semantic version.

    Possible versions list must be in the same order as the input version is structured.

    NOTE: Does not have generic prefix/suffix support, just specialized for `v` prefix

    Arguments
    ---------
    input_mod_version : str
        A version number in a str
    use_format_check : bool, optional
        Check if version format is correct, defaults to True
    possible_version_types : listlike, optional
        List indicating what each part of a semantic version represents, by default ("Major", "Minor", "Patch")
    regex_version_pattern : str, optional
        Regex pattern to check version format, defaults to looking for `(v)1.2.3`.
        Maximum number of allowed digits per semantic version with this pattern is 9.

    Returns
    -------
    current_semantic_versions : dict[version type: version]
        A dict with the broken-down semantic version components
    using_v_prefix : bool
        Useful to reconstruct version later. True if version was of style `v1.2.3` with a v
    using_v_with_space_prefix: bool
        Useful to reconstruct version later. True if version was of style `v 1.2.3` with space

    Raises
    ------
    ValueError
        Format check failed, including going over the maximum number of digits for a version number (9)

    """
    using_v_prefix = False
    using_v_with_space_prefix = False

    if use_format_check:
        if regex_version_pattern is None:
            # matches format "1.2.3" or alternatively "v1.2.3", * wildcards allowed
            regex_version_pattern = r"^v?\s?(?:(?:\d{1,9}|\*)\.){2}(?:\d{1,9}|\*)"  # yeah regex be like that
            max_digit_search = re.compile(r"\d{10,}", re.IGNORECASE)

        if not re.search(regex_version_pattern, input_mod_version, re.IGNORECASE):
            if re.search(max_digit_search, input_mod_version):
                msg = "Maximum number of digits (9) for a version number was exceeded. Why have you done this?"
                raise ValueError(msg)
            else:
                msg = f"Version format should be of type `v1.2.3`, got `{input_mod_version}`"
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
    possible_version_types: list | tuple = ("Major", "Minor", "Patch"),
    regex_version_pattern: str | None = None,
) -> tuple[dict, str]:
    """
    Take a version of the form "v1.2.3" and increment according to patch type

    Uses a regex pattern to make sure the format is correct - can be optionally skipped

    Possible versions list must be in the same order as the version is structured

    Returns dict current_semantic_versions, str updated_mod_version (concatenated from dict)

    Raises
    ------
    ValueError
        If the input version type to increment is not one of the possible semantic version choices

    """
    # break down with helper function
    current_semantic_versions, using_v_prefix, using_v_with_space_prefix = mod_version_to_dict(
        input_mod_version,
        use_format_check=use_format_check,
        possible_version_types=possible_version_types,
        regex_version_pattern=regex_version_pattern,
    )

    if patch_type not in possible_version_types:
        msg = f"Input patch type '{patch_type}' is not a possible version type, must be one of {possible_version_types}"
        raise ValueError(msg)
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
    pattern: str | list[str],
    replacestr: str | list[str],
    *,
    skip_regex_replace: bool = False,
    return_old_str: bool = False,
) -> str | tuple[str, str]:
    """
    Opens a file and replaces a part of it via regex

    Use to update version number and similar in text descriptions

    Can be used as:

    - One pattern and one replacestr. Simple search and replace.

    - List of patterns and list of replacestr. Iterates through each pair for a search and replace.

    - List of patterns to match, but only one replacestr. Uses the same replacement multiple times.

    Does NOT work with one pattern and multiple replacestr, how would you simultaneously replace one thing with multiple?

    Returns the new file string in case info from file is useful - option to also get old string

    Returns
    -------
    if return_old_str = True:

    (original_file_string, file_string) : tuple[str, str]
        The retrieved unchanged str from the file, and the new str with replacements made

    return_old_str = False:

    file_string : str
        The str that was written to file contents, has replacements made

    Raises
    ------
    TypeError
        If input pattern and replacestr types are incompatible, such that one of the usecases given above does not apply

    """
    # read into holder string for searching
    file_handle = Path.open(file_path)
    file_string: str = file_handle.read()
    file_handle.close()
    original_file_string = file_string

    if skip_regex_replace is False:
        file_string = regex_search_and_replace_with_lists_helper(pattern, replacestr, file_string)
    else:
        pass

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

    Can be used as:

    - One pattern and one replacestr. Simple search and replace.

    - List of patterns and list of replacestr. Iterates through each pair for a search and replace.

    - List of patterns to match, but only one replacestr. Uses the same replacement multiple times.

    Does NOT work with one pattern and multiple replacestr, how would you simultaneously replace one thing with multiple?

    Returns the file string with replacements made in case info from file is useful

    Raises
    ------
    TypeError
        If input pattern and replacestr types are incompatible, such that one of the usecases given above does not apply

    """
    # read template into holder string
    file_handle = Path.open(template_file_path)
    file_string = file_handle.read()
    file_handle.close()

    if skip_regex_replace is False:
        # fill in to template via regex search
        file_string = regex_search_and_replace_with_lists_helper(pattern, replacestr, file_string)
    else:
        pass

    # w writes new file
    file_handle = Path.open(generated_file_path, "w")
    file_handle.write(file_string)
    file_handle.close()

    return file_string


def regex_search_and_replace_with_lists_helper(pattern: str | list, replacestr: str | list, file_string: str) -> str:
    """
    Helper function to avoid duplicating logic in the two prior functions

    Wraps logic for unpacking lists or str input. Could probably be done with overloads, but whatever.

    Raises
    ------
    TypeError
        If input pattern and replacestr types are incompatible, such that one of the function usecases does not apply

    """
    if isinstance(pattern, list):
        if isinstance(replacestr, list):
            for selected_pattern, selected_replacementstr in zip(pattern, replacestr, strict=False):
                file_string: str = re.sub(
                    selected_pattern,
                    selected_replacementstr,
                    file_string,
                    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                )
        elif isinstance(replacestr, str):
            # reuse the same pattern multiple times
            for selected_pattern in pattern:
                file_string: str = re.sub(
                    selected_pattern,
                    replacestr,
                    file_string,
                    flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                )
        else:
            msg = f"Incompatible `replacestr` type, expected str | list[str] but got {type(replacestr)}"
            raise TypeError(msg)
    elif isinstance(pattern, str):
        if isinstance(replacestr, str):
            file_string: str = re.sub(pattern, replacestr, file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        else:
            msg = "Passed only one pattern but multiple replacement strings, types must match"
            raise TypeError(msg)
    else:
        msg = f"Input search pattern must be a single str or a list of str, got {type(pattern)}"
        raise TypeError(msg)

    return file_string


def zip_folder(folder_to_zip: Path | str, filename: Path | str) -> None:
    """
    Zip the provided directory without navigating to that directory using `pathlib` module

    Adapted from: https://stackoverflow.com/a/68817065
    """
    # Convert to Path object
    folder_to_zip = Path(folder_to_zip)

    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in folder_to_zip.rglob("*"):
            zip_file.write(entry, entry.relative_to(folder_to_zip))


def replace_markdown_list_with_bbcode(match: re.Match) -> str:
    """Helper for `convert_markdown_lists_to_bbcode` to go into `re.sub`"""
    items = match.group(1).strip().split("\n")
    # item.split[] is to preserve whitespace to the left of list item
    bbcode_items = [f"{item.split('- ')[0]}[*] {item.split('- ')[1].rstrip()}" for item in items if item.strip()]
    return "[list]\n" + "\n".join(bbcode_items) + "\n[/list]"


def convert_markdown_lists_to_bbcode(text: str) -> str:
    """
    Convert all lists in a passed markdown string to steam bbcode lists

    NOTE: collapses nested lists, full nested list support would require a full parser
    """
    # regex to capture a full markdown list
    markdown_list_pattern = re.compile(r"^[\t ]*((?:^|\n)[\t ]*- .*(?:\n[\t ]*- .*)*)", re.MULTILINE)
    # NOTE: does not make separate lists depending on indentation

    # use helper method to replace markdown lists with BBCode lists
    converted_text = markdown_list_pattern.sub(replace_markdown_list_with_bbcode, text)
    return converted_text


def replace_with_steam_formatting(markdown_string: str) -> str:
    """
    Very basic format conversion, NOT a proper parser and will not work for arbitrary markdown

    Consider using a proper full parser instead, or keep changelogs very simple and regular

    Turns something like:

    (markdown)
    ```
    ---
    ## [TEST MOD `v0.0.34`](https://github.com/Aerolfos/automated_deploy_test/releases/tag/v0.0.34):
    Fixes
    - Item 1, contains [link](https://example.com)
    - Item 2, contains **bold text**
    - Item 3, contains *italic text*
    - Item 4, contains ~~strikethrough text~~
    - Item 5, contains `code text`
    - Item 6, contains __underline text__
    - Item 7:
        ```
        multiline
        code
        block
        ```
    - Item 8
    Misc.
    - Item 1
    - Item 2
    - Item 3
        - Item 31
        - Item 32
    - Item-4
    ---
    ```

    into:

    (steam bbcode)
    ```
    [hr][/hr]
    Fixes
    [list]
    [*] Item 1, contains [url=https://example.com]link[/url]
    [*] Item 2, contains [b]bold text[/b]
    [*] Item 3, contains [i]italic text[/i]
    [*] Item 4, contains [strike]strikethrough text[/strike]
    [*] Item 5, contains [b][noparse]code text[/noparse][/b]
    [*] Item 6, contains [u]underline text[/u]
    [*] Item 7:
    [/list]
        [code]
        multiline
        code
        block
        [/code]
    [list]
    [*] Item 8
    [/list]
    Misc.
    [list]
    [*] Item 1
    [*] Item 2
    [*] Item 3
        [*] Item 31
        [*] Item 32
    [*] Item-4
    [/list]
    [hr][/hr]
    ```
    """
    # initiate
    steamed_string = markdown_string

    # simple tag replacements
    replacement_dict = {
        r"^[\t ]*---": "[hr][/hr]",  # horizontal rule
        r"^[\t ]*## .*?:\n": "",  # empty the header line with modname and mod link, we have this already from template
        r"\[([^\[]+?)\]\((.+?)\)": "[url=\\g<2>]\\g<1>[/url]",  # links
        r"(?<!\*)(\*\*)(?!\*)(.+?)(?<!\*)(\*\*)(?!\*)": "[b]\\g<2>[/b]",  # bold
        r"(?<!\*)(\*)(?!\*)(.+?)(?<!\*)(\*)(?!\*)": "[i]\\g<2>[/i]",  # italic
        r"~~(.+?)~~": "[strike]\\g<1>[/strike]",  # strikethrough
        r"`([^`\n]+?)`": "[b][noparse]\\g<1>[/noparse][/b]",  # code
        r"__(.+?)__": "[u]\\g<1>[/u]",  # underline
        r"```(.+?)```": "[code]\\g<1>[/code]",  # code block
    }
    for selected_pattern, selected_replacementstr in replacement_dict.items():
        steamed_string = re.sub(
            selected_pattern,
            selected_replacementstr,
            steamed_string,
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

    # lists
    steamed_string = convert_markdown_lists_to_bbcode(steamed_string)

    return steamed_string
