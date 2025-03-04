import argparse
import random
import re
from pathlib import Path

import pytest

import methods.input_methods as im


def test_str2bool(input_truey_strings: tuple[str], input_falsey_strings: tuple[str]) -> None:
    for v in input_truey_strings:
        assert im.str2bool(v) is True

    for v in input_falsey_strings:
        assert im.str2bool(v) is False

    with pytest.raises(argparse.ArgumentTypeError):
        im.str2bool("Some random string with actual content")

    return None


def test_parse_descriptor_to_dict(
    descriptor_test_file_path: Path,
    expected_test_descriptor_dict: dict,
    override_test_file_path: Path,
    expected_test_override_dict: dict,
) -> None:
    """Test reading from a fixture"""
    test_descriptors = {
        # test reading a descriptor file
        descriptor_test_file_path: expected_test_descriptor_dict,
        # test reading an override file
        override_test_file_path: expected_test_override_dict,
    }

    for test_path, expected_result in test_descriptors.items():
        result = im.parse_descriptor_to_dict(test_path, debug_level=0)

        for file_key, test_key in zip(result.keys(), expected_result.keys(), strict=True):
            error_msg = f"Mismatching extracted key vs test key: {file_key} =/= {test_key}"
            assert file_key == test_key, error_msg
            error_msg = f"Mismatching extracted value vs test value: {result[file_key]} =/= {expected_result[test_key]}"
            assert result[file_key] == expected_result[test_key], error_msg

        error_msg = f"Failed to match descriptor {test_path} to test \nOutput dict was: \n{result} \
            \nShould have been: \n{expected_result}"
        assert result == expected_result, error_msg

    return None


def test_create_descriptor_file() -> None:
    # TODO: This will probably need pytests file writing systems which are more complicated
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
                v_string, patch_type=curr_patch_type, use_format_check=False, possible_version_types=possible_version_types
            )
            current_expected_output = output_dict[increment_key]
            error_msg = f"Improper version increment result for key='{v_string}'\
                \nExpected:      {current_expected_output}\
                \nActual result: {result}"
            assert result == current_expected_output, error_msg

    return None


def test_search_and_replace_in_file() -> None:
    # TODO: implement
    return None


def generate_with_template_file() -> None:
    # TODO: implement
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
