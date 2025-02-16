import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#sys.path.append('../methods')
#sys.path.insert(0, os.path.dirname(__file__))

try:
    from input_methods import str2bool, get_env_variable, parse_descriptor_to_dict, mod_version_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file
except ModuleNotFoundError:
    from methods.input_methods import str2bool, get_env_variable, parse_descriptor_to_dict, mod_version_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file


def test_str2bool():
    assert str2bool("yes") == True