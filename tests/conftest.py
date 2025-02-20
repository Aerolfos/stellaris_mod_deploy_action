from pathlib import Path

import pytest


@pytest.fixture
def override_test_folder_path() -> Path:
    return Path("tests/fixtures/")

@pytest.fixture
def override_test_file_path() -> Path:
    return Path("tests/fixtures/OVERRIDE.txt")

@pytest.fixture
def descriptor_test_file_path() -> Path:
    return Path("tests/fixtures/test_descriptor.mod")

@pytest.fixture
def expected_test_descriptor_dict() -> dict[str,str]:
    return {
        "name": "test name",
        "version": "v0.2.3",
        "tags": ["Test1", "Test2", "Test3"],
        "picture": "thumbnail.png",
        "supported_version": "v0.1.*",
        "path": "mod/test/test",
        "remote_file_id": "11111",
    }

@pytest.fixture
def expected_test_override_dict() -> dict[str,str]:
    return {
        "name_override": "Display name {stellaris_version}",
        "remote_file_id_override": "314159265",
        "Test_override": "Test",
        "singleline_list_override": [" test1 ", "test2", "test3"],
        "multiline_test_override": ["test1", "test2", "test3", "test4", "test5"],
        "extra_loc_files_to_update": [
            "localisation/english/test_general_l_english.yml",
            "localisation/english/test_event_l_english.yml",
        ],
        "version_loc_key": "test_mod_version",
    }
