import sys, os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#sys.path.append('../methods')
#sys.path.insert(0, os.path.dirname(__file__))

try:
    import input_methods as im
except ModuleNotFoundError:
    import methods.input_methods as im

def test_str2bool():
    for v in ('yes', 'true', 't', 'y', '1', 'YES', 'Yes', 'True', 'TRUE'):
        assert im.str2bool(v) == True

    for v in ('no', 'false', 'f', 'n', '0', 'NO', 'No', 'False', 'FALSE'):
        assert im.str2bool(v) == False

    return None

def test_parse_descriptor_to_dict():

    # test reading a descriptor file
    test_descriptor = "fixtures/test_descriptor.mod"
    expected_test_descriptor_result = {
        "name":"test name",
        "version":"v0.2.3",
        "tags": ["Test1", "Test2", "Test3"],
        "picture":"thumbnail.png",
        "supported_version":"v0.1.*",
        "path":"mod/test/test",
        "remote_file_id":"11111",
    }

    # test reading an override file
    test_override = "fixtures/test_OVERRIDE.txt"
    expected_test_override_result = {
        'name_override': 'Display name {stellaris_version}', 
        'remote_file_id_override': '314159265', 
        'Test': 'Test',
        'singleline_list': [' test1 ' , 'test2', 'test3'],
        'multiline_test': ['test1', 'test2', 'test3', 'test4', 'test5'],
        'extra_loc_files_to_update': ["localisation/english/test_general_l_english.yml", "localisation/english/test_event_l_english.yml"],
        'version_loc_key':'test_mod_version',
    }

    test_descriptors = {
        test_descriptor:expected_test_descriptor_result,
        test_override:expected_test_override_result,
    }

    for test_path, expected_result in test_descriptors.items():
        result = im.parse_descriptor_to_dict(test_path, debug_level=0)

        for file_key, test_key in zip(result.keys(), expected_result.keys()):
            assert file_key == test_key, f"Mistmatching extracted key vs test key: {file_key} =/= {test_key}"
            assert result[file_key] == result[test_key], f"Mismatching extracted value vs test value: {result[file_key]} =/= {result[test_key]}"

        error_msg = f"Failed to match descriptor {test_path} to test \nOutput dict was: \n{result} \nShould have been: \n{expected_result}"
        assert result == expected_result, error_msg

    return None

def test_create_descriptor_file():
    return None

def test_mod_version_to_dict():

    random_1 = random.randint(0, 99999)
    random_2 = random.randint(0, 99999)
    random_3 = random.randint(0, 99999)

    # test input string as key vs expected output as value
    # output is a tuple of (current_semantic_versions, using_v_prefix, using_v_with_space_prefix)
    test_versions = {
        "v1.2.3": ({"Major":"1", "Minor":"2", "Patch":"3"}, True, False),
        "1.2.3": ({"Major":"1", "Minor":"2", "Patch":"3"}, False, False),
        "v 1.2.3": ({"Major":"1", "Minor":"2", "Patch":"3"}, True, True),
        "v12039.23929.20392": ({"Major":"12039", "Minor":"23929", "Patch":"20392"}, True, False),
        f"{random_1}.{random_2}.{random_3}": ({"Major":f"{random_1}", "Minor":f"{random_2}", "Patch":f"{random_3}"}, False, False),
        # maximum of 9 digits, this is the highest version number allowed
        "v999999999.999999999.999999999": ({"Major":"999999999", "Minor":"999999999", "Patch":"999999999"}, True, False),
        "3.14.*": ({"Major":"3", "Minor":"14", "Patch":"*"}, False, False),
        "v3.14.*": ({"Major":"3", "Minor":"14", "Patch":"*"}, True, False),
        "*.*.*":({"Major":"*", "Minor":"*", "Patch":"*"}, False, False),
        "v*.*.*":({"Major":"*", "Minor":"*", "Patch":"*"}, True, False),
        "1.*.*":({"Major":"1", "Minor":"*", "Patch":"*"}, False, False),
    }
    test_versions_fail = {
        # 1 over the max number of digits to match
        "v9999999999.9999999999.9999999999" : None,
        "vqawj.dawok.dwajc": ({"Major":"vqawj", "Minor":"dawok", "Patch":"dwajc"}, True, False),
        "1234": {},
        "klakwlk": {},
    }

    # TODO: test to check assertion works by raising error on invalid version string

    for v_string, output_dict in test_versions.items():
        result = im.mod_version_to_dict(v_string, use_format_check=True)
        assert result == output_dict, f"Failed to match {v_string} to {output_dict}, output was {result}"

    return None

def test_increment_mod_version():
    return None

def test_search_and_replace_in_file():
    return None

def generate_with_template_file():
    return None


if __name__ == "__main__":
    test_str2bool()

    test_parse_descriptor_to_dict()

    test_create_descriptor_file()

    test_mod_version_to_dict()
    
    test_increment_mod_version()
    
    test_search_and_replace_in_file()
    
    generate_with_template_file()