### Imports ###
import json
from pathlib import Path

from methods.input_methods import get_env_variable
from methods.override_methods import OverrideClass

### Settings ###
# debug level "SILENT" prints nothing, "INFO" inputs and paths, "DEBUG" prints information about parsing and processing
debug_level = "INFO"  # "SILENT", "INFO", or "DEBUG"

# whether to add a new WIP entry to changelogs for filling in
default_add_changelog_WIP_entry = True  # noqa: N816, WIP should be capitalized

### Constants ###
# constants have implications on infrastructure outside the python files
## Semantic versioning (please don't override this without good reason)
default_possible_version_types = ["Major", "Minor", "Patch"]
default_regex_version_pattern = r"^v?\s?(?:(?:\d{1,9}|\*)\.){2}(?:\d{1,9}|\*)"

## Environment variable names (passed to github action environment)
github_env_modreleasetag_name = "MOD_RELEASE_TAG"
github_env_releasetitle_name = "MOD_RELEASE_TITLE"
github_env_releasenotesfile_name = "MOD_RELEASENOTES_FILE"
github_env_descriptorfile_name = "MOD_DESCRIPTOR_FILE"
github_env_releasezipfile_name = "MOD_RELEASE_ZIP_FILE"

## Constant filenames
# technically overrideable, though it will break compatibility with other tools like the launcher, github, steamcmd etc.
default_descriptor_file_name = "descriptor.mod"
default_workshop_description_file_name = "workshop.txt"
default_readme_file_name = "README.md"
default_changelog_file_name = "CHANGELOG.md"
default_generated_release_notes_filename = "generated_release_notes.md"
default_manifest_file_name = "manifest.vdf"

## Paths
mod_folder_name = get_env_variable("modFolderName", None, debug_level=debug_level)
# bypass if file ran directly as a standalone
if __name__ == "__main__":
    mod_folder_name = "Placeholder"

if not mod_folder_name:
    msg = "Mod folder name is missing or incomplete, must set an env variable with calling Github repo name"
    raise ValueError(msg)

mod_repo_name = mod_folder_name  # NOTE part of expected `modname/modname/common` structure

# cwd is set to where the python file is,
# which should be next to the folder with the mod files from the originating mod repository
mod_github_folder_path = (Path.cwd() / f"../{mod_folder_name}").resolve()
# and the folder with the actual game mod files (nested one down from github)
mod_files_folder_path = mod_github_folder_path / mod_folder_name

# file to output the current set of overrideable parameters for convenience
# NOTE: files for the tool repo don't get committed during a workflow run
# (not that external parties running the tool would be allowed to)
# so this file is generated when manually running this script from the dev side
overrideable_parameters_file_path = Path.cwd() / ".github/" / "overrideable_parameters.json"

### Defaults ###
# merely convenient defaults for python script, can be changed
## Filenames
default_release_note_template_filename = "release_note_template.md"
default_release_note_template_no_changelog_filename = "release_note_template_no_changelog.md"
default_workshop_change_note_template_filename = "workshop_change_note_template.md"

# file for giving (potential) extra information to web tools
default_webhook_json_file_path = mod_github_folder_path / ".github/" / "supported_stellaris_version.json"

## Regex search patterns
# loc_something:0 "something"
# 0 code intentional since numbers other than 0 are generated or messed with by some tool, usually
# generic localization pattern matching
default_loc_key_pattern = '(\\s{}:0\\s").+?(")'  # use with .format(loc_key)

# "Supports Stellaris version: 1.2.x" with version number bolded in steam BBcode
default_workshop_desc_version_pattern = r"(Supports Stellaris version: \[b\]).+?(\[/b\])"

# "Supports Stellaris version: `1.2.x`" with version number using code embed in markdown
default_readme_version_pattern = r"(Supports Stellaris version: \`).+?(\`)"

# "https://github.com/username/repo_name/releases/tag/v1.2.3"
# expects to be filled in with {username/repo_name} and {release-tag} from script
default_github_release_link_pattern = r"https://github.com/{}/releases/tag/{}"

# search patterns for extracting changelogs - expects latest changes to be under "WIP"
# changelog entries by default are of the form:
"""
---
## ModName Version `WIP`:
- Latest
- Change
- Entries
---

[Older versions]
"""
default_changelog_search_pattern = r"(^---\n)(##\s)(.+?\s`)WIP(`)(:\n)(.*?)(^---$)"
# regex r"(^---\n)(## .+?\s`.{1,13}`:\n)(.*?)(^---$)" matches arbitrary version numbers
default_template_search_pattern = r"(^---\n)(\nChanges\n\n)(^---$)"
default_template_insert_version_pattern = r"(##\s)(Supports Stellaris version:\s\`).+?(\`)"

# for pushing to workshop, changelog file has been changed by github release script
# now the full changelog will be (placeholder may not be present depending on settings):
"""
# Changes for [ModName](https://steamcommunity.com/sharedfiles/filedetails/?id=mod_workshop_id)

---
## ModName `WIP`:
- Newest changes
---

---
## [ModName `v1.2.3`](https://github.com/UserName/mod_name/releases/tag/v1.2.3):
- Latest
- Change
- Entries
---

[Even older versions]
"""
# this pattern will search the arbitrary, already linked entries, and extract changes for one specific mod version
# note the {}, for use with .format to insert a version number to search for
# just paste this in regex101.com don't try to understand the regex directly
default_versioned_changelog_entry_search_pattern = r"(^---\n)(##\s)(\[.+?\s`){}(`)(\]\(.+?\))(:\n)(.*?)(^---$)"
# for replacing what is inside the horizontal rules in the workshop changenote template
default_workshop_template_search_pattern = r"(^\[hr\]\[/hr\]\n)(.+?\n)(^\[hr\]\[/hr\]$)"

### Overrides ###
Overrides = OverrideClass(mod_github_folder_path, debug_level=debug_level)
overrides_enabled = Overrides.overrides_enabled

## Setting overrides
add_changelog_WIP_entry = Overrides.get_parameter("add_changelog_WIP_entry", default_add_changelog_WIP_entry)  # noqa: N816
possible_version_types = Overrides.get_parameter("possible_version_types", default_possible_version_types)
regex_version_pattern = Overrides.get_parameter("regex_version_pattern", default_regex_version_pattern)

## Path overrides
descriptor_file_name = Overrides.get_parameter("descriptor_file_name", default_descriptor_file_name)
# note, descriptor is with mod files, not in higher level repository
descriptor_file_path = mod_files_folder_path / descriptor_file_name
workshop_description_file_name = Overrides.get_parameter(
    "workshop_description_file_name",
    default_workshop_description_file_name,
)
workshop_description_file_path = mod_github_folder_path / workshop_description_file_name
readme_file_name = Overrides.get_parameter("readme_file_name", default_readme_file_name)
readme_file_path = mod_github_folder_path / readme_file_name
changelog_file_name = Overrides.get_parameter("changelog_file_name", default_changelog_file_name)
changelog_file_path = mod_github_folder_path / changelog_file_name

webhook_json_file_path = Overrides.get_parameter("webhook_json_file_path", default_webhook_json_file_path)

# temp files used by script, kept out of mod files repository so as to not be committed
generated_release_notes_filename = Overrides.get_parameter(
    "generated_release_notes_filename",
    default_generated_release_notes_filename,
)
generated_release_notes_file_path = Path.cwd() / generated_release_notes_filename
manifest_file_name = Overrides.get_parameter("manifest_file_name", default_manifest_file_name)
manifest_file_path = Path.cwd() / manifest_file_name

# template files
release_note_template_filename = Overrides.get_parameter(
    "release_note_template_filename",
    default_release_note_template_filename,
)
release_note_template_overriden = Overrides.overriden_params["release_note_template_filename"]
# default template file is generic and comes from the deploy repo
# but otherwise, check user provided one (which can only come from *their* repo)
if not release_note_template_overriden:
    release_note_template_file_path = Path.cwd() / "templates/" / release_note_template_filename
else:
    release_note_template_file_path = mod_github_folder_path / release_note_template_filename

# no changelog version
release_note_template_no_changelog_filename = Overrides.get_parameter(
    "release_note_template_no_changelog_filename",
    default_release_note_template_no_changelog_filename,
)
release_note_template_no_changelog_overriden = Overrides.overriden_params["release_note_template_no_changelog_filename"]
# same as above
if not release_note_template_no_changelog_overriden:
    release_note_template_no_changelog_file_path = Path.cwd() / "templates/" / release_note_template_no_changelog_filename
else:
    release_note_template_no_changelog_file_path = mod_github_folder_path / release_note_template_no_changelog_filename

# workshop change note, same as above
workshop_change_note_template_filename = Overrides.get_parameter(
    "workshop_change_note_template_filename",
    default_workshop_change_note_template_filename,
)
workshop_change_note_template_overriden = Overrides.overriden_params["workshop_change_note_template_filename"]
if not workshop_change_note_template_overriden:
    workshop_change_note_template_file_path = Path.cwd() / "templates/" / workshop_change_note_template_filename
else:
    workshop_change_note_template_file_path = mod_github_folder_path / workshop_change_note_template_filename

## Descriptor overrides
# can supply overrides to the parsed descriptor from the mod github
descriptor_override_name = Overrides.get_parameter("name", None)
descriptor_override_version = Overrides.get_parameter("version", None)
descriptor_override_tags = Overrides.get_parameter("tags", None)
descriptor_override_picture = Overrides.get_parameter("picture", None)
descriptor_override_supported_version = Overrides.get_parameter("supported_version", None)
descriptor_override_path = Overrides.get_parameter("path", None)
descriptor_override_remote_file_id = Overrides.get_parameter("remote_file_id", None)

## Search pattern overrides
loc_key_pattern = Overrides.get_parameter("loc_key_pattern", default_loc_key_pattern)
workshop_desc_version_pattern = Overrides.get_parameter(
    "workshop_desc_version_pattern",
    default_workshop_desc_version_pattern,
)
readme_version_pattern = Overrides.get_parameter("readme_version_pattern", default_readme_version_pattern)
github_release_link_pattern = Overrides.get_parameter(
    "github_release_link_pattern",
    default_github_release_link_pattern,
)
changelog_search_pattern = Overrides.get_parameter("changelog_search_pattern", default_changelog_search_pattern)
template_search_pattern = Overrides.get_parameter("template_search_pattern", default_template_search_pattern)
template_insert_version_pattern = Overrides.get_parameter(
    "template_insert_version_pattern",
    default_template_insert_version_pattern,
)

versioned_changelog_entry_search_pattern = Overrides.get_parameter(
    "versioned_changelog_entry_search_pattern",
    default_versioned_changelog_entry_search_pattern,
)
workshop_template_search_pattern = Overrides.get_parameter(
    "workshop_template_search_pattern",
    default_workshop_template_search_pattern,
)

## Custom logic for handling overriding of loc keys, potentially from multiple files
if not Overrides.overrides_enabled:
    loc_files_list = []
    version_loc_key = None
else:
    try:
        loc_files_list = Overrides.override_dict["extra_loc_files_to_update"]  # list of files
        version_loc_key = Overrides.override_dict["version_loc_key"]  # loc key to look for, inserted in generic search pattern
    except KeyError:
        loc_files_list = []
        version_loc_key = None

if __name__ == "__main__":
    # save a json with the list of parameters this script supports for overrides
    params_dict = {"overrideable_parameter_names": [param + "_override" for param in Overrides.overriden_params]}
    params_dict["special_params"] = ["extra_loc_files_to_update", "version_loc_key"]
    with Path.open(overrideable_parameters_file_path, "w") as params_json_file_object:
        json.dump(params_dict, params_json_file_object, indent=4)
