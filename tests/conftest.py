from pathlib import Path

import pytest  # ty: ignore ty tooltip fails on a dev dependency?


@pytest.fixture
def input_truey_strings() -> tuple:
    return ("yes", "true", "t", "y", "1", "YES", "Yes", "True", "TRUE")


@pytest.fixture
def input_falsey_strings() -> tuple:
    return ("no", "false", "f", "n", "0", "NO", "No", "False", "FALSE")


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
def expected_test_descriptor_dict() -> dict[str, str]:
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
def input_test_descriptor_dict(expected_test_descriptor_dict: dict[str, str]) -> dict[str, str]:
    return expected_test_descriptor_dict


@pytest.fixture
def expected_test_override_dict() -> dict[str, str]:
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


@pytest.fixture
def expected_test_overriden_params_dict() -> dict[str, bool]:
    return {
        "name": True,
        "version": False,
        "singleline_list": True,
        "multiline_test": True,
        "picture": False,
        "supported_version": False,
        "path": False,
        "remote_file_id": True,
    }


@pytest.fixture
def input_example_changelog_file_str() -> str:
    test_str = """
---
## ModName Version `WIP`:
- Latest
- Change
- Entries
---

[Older versions]
"""
    return test_str


@pytest.fixture
def expected_modified_changelog_file_str() -> str:
    test_str = """
---
## [ModName Version `v1.2.3`](https://github.com/test/releases/tag/v1.2.3):
- Latest
- Change
- Entries
---

[Older versions]
"""
    return test_str


@pytest.fixture
def expected_double_modified_changelog_file_str() -> str:
    test_str = """
---
## [ModName Version `v1.2.3`](https://github.com/test/releases/tag/v1.2.3):
- Some new changelog text has been written here
---

[Older versions]
"""
    return test_str


@pytest.fixture
def input_example_versions_file_str() -> str:
    test_str = """
## ModName Version `?.?.?`:
Mod version: `?.?.?`
Mod version: [b]?.?.?[/b]
"""
    return test_str


@pytest.fixture
def expected_multipattern_modified_changelog_file_str() -> str:
    test_str = """
## ModName Version `v1.2.3`:
Mod version: `v1.2.3`
Mod version: [b]v1.2.3[/b]
"""
    return test_str


@pytest.fixture
def input_markdown_lists() -> str:
    # (markdown)
    return """
Here is a markdown list to convert:

- item1
- item2
- item3

Another list:

- another1
- another2
"""


@pytest.fixture
def expected_bbcode_converted_lists() -> str:
    # (steam bbcode)
    return """
Here is a markdown list to convert:
[list]
[*] item1
[*] item2
[*] item3
[/list]

Another list:
[list]
[*] another1
[*] another2
[/list]
"""


@pytest.fixture
def input_markdown_to_steam_conversion() -> str:
    # (markdown)
    return """
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
"""


@pytest.fixture
def expected_markdown_to_steam_conversion() -> str:
    # (steam bbcode)
    return """
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
"""
