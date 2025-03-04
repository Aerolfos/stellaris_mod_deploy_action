from pathlib import Path

import methods.override_methods as om


def test_override_class(
    override_test_folder_path: Path,
    expected_test_override_dict: dict[str, str],
    expected_test_overriden_params_dict: dict[str, bool],
) -> None:
    # test reading an override file
    overrides = om.OverrideClass(override_test_folder_path, debug_level=0)
    assert overrides.overrides_enabled is True

    result = overrides.override_dict
    for file_key, test_key in zip(result.keys(), expected_test_override_dict.keys(), strict=True):
        assert file_key == test_key, f"Mismatching extracted key vs test key: {file_key} =/= {test_key}"
        assert result[file_key] == expected_test_override_dict[test_key], (
            f"Mismatching extracted value vs test value: {result[file_key]} =/= {expected_test_override_dict[test_key]}"
        )

    # based on what is in dict above, tests whether override or skip happens as expected
    descriptor_override_name = overrides.get_parameter("name", None)
    assert descriptor_override_name == "Display name {stellaris_version}"
    descriptor_override_version = overrides.get_parameter("version", None)
    assert descriptor_override_version is None
    singleline_list = overrides.get_parameter("singleline_list", None)
    assert singleline_list == [" test1 ", "test2", "test3"]
    multiline_test = overrides.get_parameter("multiline_test", None)
    assert multiline_test == ["test1", "test2", "test3", "test4", "test5"]
    descriptor_override_picture = overrides.get_parameter("picture", None)
    assert descriptor_override_picture is None
    descriptor_override_supported_version = overrides.get_parameter("supported_version", None)
    assert descriptor_override_supported_version is None
    descriptor_override_path = overrides.get_parameter("path", None)
    assert descriptor_override_path is None
    descriptor_override_remote_file_id = overrides.get_parameter("remote_file_id", None)
    assert descriptor_override_remote_file_id == "314159265"

    overriden_params_dict = overrides.overriden_params
    for override_key, test_key in zip(overriden_params_dict.keys(), expected_test_overriden_params_dict.keys(), strict=True):
        assert override_key == test_key, f"Mismatching extracted key vs test key: {override_key} =/= {test_key}"
        assert overriden_params_dict[override_key] == expected_test_overriden_params_dict[test_key], (
            f"Mismatching override active value vs test value: \
                {overriden_params_dict[override_key]} =/= {expected_test_overriden_params_dict[test_key]}"
        )

    # test a nonexistent file, should skip gracefully
    test_override2 = Path("tests/fixtures/None/")
    overrides2 = om.OverrideClass(test_override2, debug_level=0)
    assert overrides2.overrides_enabled is False

    descriptor_override_name = overrides2.get_parameter("name", None)
    assert descriptor_override_name is None

    return None
