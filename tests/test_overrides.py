import os
import sys
import random

from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import override_methods as om
except ModuleNotFoundError:
    import methods.override_methods as om

def test_override_class():
    # test reading an override file
    test_override = Path("fixtures/")
    expected_test_override_result = {
        'name_override': 'Display name {stellaris_version}', 
        'remote_file_id_override': '314159265', 
        'Test_override': 'Test',
        'singleline_list_override': [' test1 ' , 'test2', 'test3'],
        'multiline_test_override': ['test1', 'test2', 'test3', 'test4', 'test5'],
        'extra_loc_files_to_update': ["localisation/english/test_general_l_english.yml", "localisation/english/test_event_l_english.yml"],
        'version_loc_key':'test_mod_version',
    }
    
    Overrides = om.OverrideClass(test_override, debug_level=0)
    assert Overrides.overrides_enabled is True

    result = Overrides.override_dict
    for file_key, test_key in zip(result.keys(), expected_test_override_result.keys()):
        assert file_key == test_key, f"Mismatching extracted key vs test key: {file_key} =/= {test_key}"
        assert result[file_key] == result[test_key], f"Mismatching extracted value vs test value: {result[file_key]} =/= {result[test_key]}"

    # based on what is in dict above, tests whether override or skip happens as expected
    descriptor_override_name = Overrides.get_parameter("name", None)
    assert descriptor_override_name == 'Display name {stellaris_version}'
    descriptor_override_version = Overrides.get_parameter("version", None)
    assert descriptor_override_version is None
    singleline_list = Overrides.get_parameter("singleline_list", None)
    assert singleline_list == [' test1 ' , 'test2', 'test3']
    multiline_test = Overrides.get_parameter("multiline_test", None)
    assert multiline_test == ['test1', 'test2', 'test3', 'test4', 'test5']
    descriptor_override_picture = Overrides.get_parameter("picture", None)
    assert descriptor_override_picture is None
    descriptor_override_supported_version = Overrides.get_parameter("supported_version", None)
    assert descriptor_override_supported_version is None
    descriptor_override_path = Overrides.get_parameter("path", None)
    assert descriptor_override_path is None
    descriptor_override_remote_file_id = Overrides.get_parameter("remote_file_id", None)
    assert descriptor_override_remote_file_id == "314159265"

    # test a nonexistent file, should skip gracefully
    test_override2 = Path("fixtures/None/")
    Overrides2 = om.OverrideClass(test_override2, debug_level=0)
    assert Overrides2.overrides_enabled is False

    descriptor_override_name = Overrides2.get_parameter("name", None)
    assert descriptor_override_name is None

    return None

if __name__ == "__main__":
    test_override_class()
