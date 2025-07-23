import argparse
import random
import re
from pathlib import Path

import pytest  # ty: ignore ty tooltip fails on a dev dependency?

import methods.input_methods as im


def test_str2bool(input_truey_strings: tuple[str], input_falsey_strings: tuple[str]) -> None:
    for v in input_truey_strings:
        assert im.str2bool(v) is True

    for v in input_falsey_strings:
        assert im.str2bool(v) is False

    assert im.str2bool(None) is False

    with pytest.raises(argparse.ArgumentTypeError):
        im.str2bool("Some random string with actual content")

    return None


def test_parse_descriptor_to_dict(
    descriptor_test_file_path: Path,
    expected_test_descriptor_dict: dict[str, str],
    override_test_file_path: Path,
    expected_test_override_dict: dict[str, str],
) -> None:
    """Test reading from a fixture"""
    test_descriptors = {
        # test reading a descriptor file
        descriptor_test_file_path: expected_test_descriptor_dict,
        # test reading an override file
        override_test_file_path: expected_test_override_dict,
    }

    for test_path, expected_result in test_descriptors.items():
        result = im.parse_descriptor_to_dict(test_path, debug_level="INFO")

        for file_key, test_key in zip(result.keys(), expected_result.keys(), strict=True):
            error_msg = f"Mismatching extracted key vs test key: {file_key} =/= {test_key}"
            assert file_key == test_key, error_msg
            error_msg = f"Mismatching extracted value vs test value: {result[file_key]} =/= {expected_result[test_key]}"
            assert result[file_key] == expected_result[test_key], error_msg

        error_msg = f"Failed to match descriptor {test_path} to test \nOutput dict was: \n{result} \
            \nShould have been: \n{expected_result}"
        assert result == expected_result, error_msg

    return None


def test_create_descriptor_file(
    input_test_descriptor_dict: dict[str, str],
    tmp_path: Path,
    descriptor_test_file_path: Path,
) -> None:
    # since we previously tested if a file output matches a predefined dict,
    # then it follows that writing the predefined dict to file via this method should match the test file
    output_file_path = tmp_path / "output_descriptor.mod"
    im.create_descriptor_file(input_test_descriptor_dict, output_file_path)

    assert output_file_path.read_text() == descriptor_test_file_path.read_text()

    return None


def test_mod_version_to_dict() -> None:
    random_1 = random.randint(0, 99998)
    random_2 = random.randint(0, 99998)
    random_3 = random.randint(0, 99998)

    # test input string as key vs expected output as value
    # output is a tuple of (current_semantic_versions, using_v_prefix, using_v_with_space_prefix)
    test_versions = {
        "v1.2.3": ({"Major": "1", "Minor": "2", "Patch": "3"}, True, False),
        "1.2.3": ({"Major": "1", "Minor": "2", "Patch": "3"}, False, False),
        "v 1.2.3": ({"Major": "1", "Minor": "2", "Patch": "3"}, True, True),
        "v12039.23929.20392": ({"Major": "12039", "Minor": "23929", "Patch": "20392"}, True, False),
        f"{random_1}.{random_2}.{random_3}": (
            {"Major": f"{random_1}", "Minor": f"{random_2}", "Patch": f"{random_3}"},
            False,
            False,
        ),
        # maximum of 9 digits, this is the highest version number allowed
        "v999999999.999999999.999999999": (
            {"Major": "999999999", "Minor": "999999999", "Patch": "999999999"},
            True,
            False,
        ),
        "3.14.*": ({"Major": "3", "Minor": "14", "Patch": "*"}, False, False),
        "v3.14.*": ({"Major": "3", "Minor": "14", "Patch": "*"}, True, False),
        "*.*.*": ({"Major": "*", "Minor": "*", "Patch": "*"}, False, False),
        "v*.*.*": ({"Major": "*", "Minor": "*", "Patch": "*"}, True, False),
        "1.*.*": ({"Major": "1", "Minor": "*", "Patch": "*"}, False, False),
    }

    for v_string, output_dict in test_versions.items():
        result = im.mod_version_to_dict(v_string, use_format_check=True)
        error_msg = f"Failed to match {v_string} to {output_dict}, output was {result}"
        assert result == output_dict, error_msg

    # test errors correctly raised on invalid version strings
    test_versions_fail_length = [
        # 1 over the max number of digits to match
        "v9999999999.9999999999.9999999999",
    ]
    for v_string in test_versions_fail_length:
        err_msg_length = re.escape("Maximum number of digits (9) for a version number was exceeded.")
        with pytest.raises(ValueError, match=err_msg_length) as excinfo:
            result = im.mod_version_to_dict(v_string, use_format_check=True)

    test_versions_fail_format = [
        "vqawj.dawok.dwajc",
        "1234",
        "klakwlk",
    ]
    for v_string in test_versions_fail_format:
        err_msg_format = f"Version format should be of type `v1.2.3`, got `{v_string}`"
        with pytest.raises(ValueError, match=err_msg_format) as excinfo:
            result = im.mod_version_to_dict(v_string, use_format_check=True)

        assert err_msg_format in str(excinfo.value)

    return None


def test_increment_mod_version() -> None:
    random_1 = random.randint(0, 99998)
    random_2 = random.randint(0, 99998)
    random_3 = random.randint(0, 99998)

    increment_list = ["increment_major", "increment_minor", "increment_patch"]
    possible_version_types = ("Major", "Minor", "Patch")

    test_increment_versions = {
        "v1.2.3": {
            "increment_major": ({"Major": "2", "Minor": "0", "Patch": "0"}, "v2.0.0"),
            "increment_minor": ({"Major": "1", "Minor": "3", "Patch": "0"}, "v1.3.0"),
            "increment_patch": ({"Major": "1", "Minor": "2", "Patch": "4"}, "v1.2.4"),
        },
        "1.2.3": {
            "increment_major": ({"Major": "2", "Minor": "0", "Patch": "0"}, "2.0.0"),
            "increment_minor": ({"Major": "1", "Minor": "3", "Patch": "0"}, "1.3.0"),
            "increment_patch": ({"Major": "1", "Minor": "2", "Patch": "4"}, "1.2.4"),
        },
        "v 1.2.3": {
            "increment_major": ({"Major": "2", "Minor": "0", "Patch": "0"}, "v 2.0.0"),
            "increment_minor": ({"Major": "1", "Minor": "3", "Patch": "0"}, "v 1.3.0"),
            "increment_patch": ({"Major": "1", "Minor": "2", "Patch": "4"}, "v 1.2.4"),
        },
        "v12039.23929.20392": {
            "increment_major": ({"Major": "12040", "Minor": "0", "Patch": "0"}, "v12040.0.0"),
            "increment_minor": ({"Major": "12039", "Minor": "23930", "Patch": "0"}, "v12039.23930.0"),
            "increment_patch": ({"Major": "12039", "Minor": "23929", "Patch": "20393"}, "v12039.23929.20393"),
        },
        f"{random_1}.{random_2}.{random_3}": {
            "increment_major": (
                {"Major": f"{random_1 + 1}", "Minor": f"{0}", "Patch": f"{0}"},
                f"{random_1 + 1}.{0}.{0}",
            ),
            "increment_minor": (
                {"Major": f"{random_1}", "Minor": f"{random_2 + 1}", "Patch": f"{0}"},
                f"{random_1}.{random_2 + 1}.{0}",
            ),
            "increment_patch": (
                {"Major": f"{random_1}", "Minor": f"{random_2}", "Patch": f"{random_3 + 1}"},
                f"{random_1}.{random_2}.{random_3 + 1}",
            ),
        },
        # maximum of 9 digits, this is the highest version number allowed
        "v999999999.999999999.999999999": {
            "increment_major": (
                {"Major": "1000000000", "Minor": "0", "Patch": "0"},
                "v1000000000.0.0",
            ),
            "increment_minor": (
                {"Major": "999999999", "Minor": "1000000000", "Patch": "0"},
                "v999999999.1000000000.0",
            ),
            "increment_patch": (
                {"Major": "999999999", "Minor": "999999999", "Patch": "1000000000"},
                "v999999999.999999999.1000000000",
            ),
        },
        "3.14.*": {
            "increment_major": ({"Major": "4", "Minor": "0", "Patch": "*"}, "4.0.*"),
            "increment_minor": ({"Major": "3", "Minor": "15", "Patch": "*"}, "3.15.*"),
            "increment_patch": ({"Major": "3", "Minor": "14", "Patch": "*"}, "3.14.*"),
        },
        "v3.14.*": {
            "increment_major": ({"Major": "4", "Minor": "0", "Patch": "*"}, "v4.0.*"),
            "increment_minor": ({"Major": "3", "Minor": "15", "Patch": "*"}, "v3.15.*"),
            "increment_patch": ({"Major": "3", "Minor": "14", "Patch": "*"}, "v3.14.*"),
        },
        "*.*.*": {
            "increment_major": ({"Major": "*", "Minor": "*", "Patch": "*"}, "*.*.*"),
            "increment_minor": ({"Major": "*", "Minor": "*", "Patch": "*"}, "*.*.*"),
            "increment_patch": ({"Major": "*", "Minor": "*", "Patch": "*"}, "*.*.*"),
        },
        "v*.*.*": {
            "increment_major": ({"Major": "*", "Minor": "*", "Patch": "*"}, "v*.*.*"),
            "increment_minor": ({"Major": "*", "Minor": "*", "Patch": "*"}, "v*.*.*"),
            "increment_patch": ({"Major": "*", "Minor": "*", "Patch": "*"}, "v*.*.*"),
        },
        "1.*.*": {
            "increment_major": ({"Major": "2", "Minor": "*", "Patch": "*"}, "2.*.*"),
            "increment_minor": ({"Major": "1", "Minor": "*", "Patch": "*"}, "1.*.*"),
            "increment_patch": ({"Major": "1", "Minor": "*", "Patch": "*"}, "1.*.*"),
        },
    }

    # match a result dict for all possible patch types for each given input string
    for v_string, output_dict in test_increment_versions.items():
        for increment_key, curr_patch_type in zip(increment_list, possible_version_types, strict=True):
            result = im.increment_mod_version(v_string, patch_type=curr_patch_type, use_format_check=True)
            current_expected_output = output_dict[increment_key]
            error_msg = f"Improper version increment result for key='{v_string}'\
                \nExpected:      {current_expected_output}\
                \nActual result: {result}"
            assert result == current_expected_output, error_msg

    # check with different versioning systems
    increment_list = ["increment_major", "increment_build"]
    possible_version_types = ("Major", "Build")
    test_increment_versions = {
        "v1.120": {
            "increment_major": ({"Major": "2", "Build": "0"}, "v2.0"),
            "increment_build": ({"Major": "1", "Build": "121"}, "v1.121"),
        },
    }

    for v_string, output_dict in test_increment_versions.items():
        for increment_key, curr_patch_type in zip(increment_list, possible_version_types, strict=True):
            result = im.increment_mod_version(
                v_string,
                patch_type=curr_patch_type,
                use_format_check=False,
                possible_version_types=possible_version_types,
            )
            current_expected_output = output_dict[increment_key]
            error_msg = f"Improper version increment result for key='{v_string}'\
                \nExpected:      {current_expected_output}\
                \nActual result: {result}"
            assert result == current_expected_output, error_msg

    return None


def helper_search_and_replace_file_asserts(
    input_example_str: str,
    retrieved_file_str: str,
    output_file_path: Path,
    new_file_str: str,
    expected_modified_file_str: str,
) -> bool:
    """Helper function to avoid repeating asserts"""
    error_msg = f"Did not succesfully return old string from file\
                \nExpected:      {input_example_str}\
                \nActual result: {retrieved_file_str}"
    assert input_example_str == retrieved_file_str, error_msg

    str_from_file: str = output_file_path.read_text()
    error_msg = f"Modified string returned from method does not match string written to file\
                \nExpected:      {new_file_str}\
                \nActual result: {str_from_file}"
    assert new_file_str == str_from_file, error_msg

    str_from_file: str = output_file_path.read_text()
    error_msg = f"Written file does not match expected modified changelog text\
                \nExpected:      {expected_modified_file_str}\
                \nActual result: {str_from_file}"
    assert expected_modified_file_str == str_from_file, error_msg

    return True


def test_search_and_replace_in_file(  # noqa: PLR0913
    tmp_path: Path,
    input_example_changelog_file_str: str,
    input_example_versions_file_str: str,
    expected_modified_changelog_file_str: str,
    expected_double_modified_changelog_file_str: str,
    expected_multipattern_modified_changelog_file_str: str,
) -> None:
    output_file_path: Path = tmp_path / "test.txt"
    output_file_path.write_text(input_example_changelog_file_str)

    # changelog entry with WIP
    changelog_search_pattern: str = r"(^---\n)(##\s)(.+?\s`)WIP(`)(:\n)(.*?)(^---$)"
    # changelog entry with version and a link added
    default_versioned_changelog_entry_search_pattern: str = r"(^---\n)(##\s)(\[.+?\s`)({})(`)(\]\(.+?\))(:\n)(.*?)(^---$)"

    updated_mod_version: str = "v1.2.3"
    github_release_link: str = f"https://github.com/test/releases/tag/{updated_mod_version}"
    versioned_changelog_entry_search_pattern: str = default_versioned_changelog_entry_search_pattern.format(updated_mod_version)

    changelog_replace: str = f"\\g<1>\\g<2>[\\g<3>{updated_mod_version}\\g<4>]({github_release_link})\\g<5>\\g<6>\\g<7>"

    # needs an explicit newline, the search pattern eats a newline
    new_change_notes: str = "- Some new changelog text has been written here\n"
    # groups based on default_versioned_changelog_entry_search_pattern
    changelog_notes_replace: str = f"\\g<1>\\g<2>\\g<3>\\g<4>\\g<5>\\g<6>\\g<7>{new_change_notes}\\g<9>"

    ## one to one pattern to replace
    retrieved_file_str, new_file_str = im.search_and_replace_in_file(
        output_file_path, changelog_search_pattern, changelog_replace, skip_regex_replace=False, return_old_str=True
    )

    helper_function_return = helper_search_and_replace_file_asserts(
        input_example_changelog_file_str,
        retrieved_file_str,
        output_file_path,
        new_file_str,
        expected_modified_changelog_file_str,
    )
    assert helper_function_return is True

    ## two to two patterns to replace
    output_file_path.write_text(input_example_changelog_file_str)

    # first replaces WIP entry header with link and version number as above
    # then finds the entry via version number and overwrites the notes inside it
    retrieved_file_str, new_file_str = im.search_and_replace_in_file(
        output_file_path,
        [changelog_search_pattern, versioned_changelog_entry_search_pattern],
        [changelog_replace, changelog_notes_replace],
        skip_regex_replace=False,
        return_old_str=True,
    )

    helper_function_return = helper_search_and_replace_file_asserts(
        input_example_changelog_file_str,
        retrieved_file_str,
        output_file_path,
        new_file_str,
        expected_double_modified_changelog_file_str,
    )
    assert helper_function_return is True

    ## three patterns, one replace for all
    output_file_path.write_text(input_example_versions_file_str)

    # replace three kinds of strings with version numbers with new version number (always the same version number)
    md_header_version_pattern = r"(## ModName Version \`).+?(\`:)"
    md_version_pattern = r"(Mod version: \`).+?(\`)"
    steam_version_pattern = r"(Mod version: \[b\]).+?(\[/b\])"

    version_number_replaced = f"\\g<1>{updated_mod_version}\\g<2>"

    retrieved_file_str, new_file_str = im.search_and_replace_in_file(
        output_file_path,
        [md_header_version_pattern, md_version_pattern, steam_version_pattern],
        version_number_replaced,
        skip_regex_replace=False,
        return_old_str=True,
    )

    helper_function_return = helper_search_and_replace_file_asserts(
        input_example_versions_file_str,
        retrieved_file_str,
        output_file_path,
        new_file_str,
        expected_multipattern_modified_changelog_file_str,
    )
    assert helper_function_return is True

    ## test errors and skip functionality
    output_file_path.write_text(input_example_versions_file_str)

    retrieved_file_str, new_file_str = im.search_and_replace_in_file(
        output_file_path,
        md_header_version_pattern,
        version_number_replaced,
        skip_regex_replace=True,
        return_old_str=True,
    )

    # assert that input is equal to output
    helper_function_return = helper_search_and_replace_file_asserts(
        input_example_versions_file_str,
        retrieved_file_str,
        output_file_path,
        new_file_str,
        input_example_versions_file_str,
    )
    assert helper_function_return is True

    with pytest.raises(TypeError):
        # error from multiple replacements to one pattern
        # arguments dont really matter
        retrieved_file_str, new_file_str = im.search_and_replace_in_file(
            output_file_path,
            "search",
            ["replace1", "replace2"],
            skip_regex_replace=False,
            return_old_str=True,
        )

    with pytest.raises(TypeError):
        # error from wrong types
        retrieved_file_str, new_file_str = im.search_and_replace_in_file(
            output_file_path,
            10,  # ty: ignore wrong arg on purpose
            ["replace1", "replace2"],
            skip_regex_replace=False,
            return_old_str=True,
        )

    with pytest.raises(TypeError):
        # error from wrong types
        retrieved_file_str, new_file_str = im.search_and_replace_in_file(
            output_file_path,
            "search",
            10,  # ty: ignore wrong arg on purpose
            skip_regex_replace=False,
            return_old_str=True,
        )

    return None


def test_generate_with_template_file(tmp_path: Path, input_example_changelog_file_str: str) -> None:
    # TODO: implement
    output_file_path = tmp_path / "test.txt"
    output_file_path.write_text(input_example_changelog_file_str)

    default_regex_version_pattern = r"^v?\s?(?:(?:\d{1,9}|\*)\.){2}(?:\d{1,9}|\*)"

    # pattern
    supported_stellaris_version_display = "3.14.x"
    new_version_line = f"\\g<1>{supported_stellaris_version_display}\\g<2>"

    # test skip
    im.generate_with_template_file(
        output_file_path, output_file_path, default_regex_version_pattern, new_version_line, skip_regex_replace=True
    )
    return None


def test_convert_markdown_lists_to_bbcode(input_markdown_lists: str, expected_bbcode_converted_lists: str) -> None:
    output_str = im.convert_markdown_lists_to_bbcode(input_markdown_lists)
    error_msg = f"Conversion of input markdown lists does not match expected steam bbcode lists output\
        \nExpected output: \n{expected_bbcode_converted_lists}\
        \nActual output: \n{output_str}"
    assert output_str == expected_bbcode_converted_lists, error_msg

    return None


def test_replace_with_steam_formatting(
    input_markdown_to_steam_conversion: str,
    expected_markdown_to_steam_conversion: str,
) -> None:
    output_str = im.replace_with_steam_formatting(input_markdown_to_steam_conversion)
    error_msg = f"Conversion of input markdown formatting does not match expected steam bbcode output\
        \nExpected output: \n{expected_markdown_to_steam_conversion}\
        \nActual output: \n{output_str}"
    assert output_str == expected_markdown_to_steam_conversion, error_msg

    return None


# TODO: maybe
# does zip folder method need tests?
# check code coverage? not sure how that works
