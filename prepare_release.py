### Imports ###
import argparse
import os
import re
from pathlib import Path

import constants_and_overrides as cao
from methods.input_methods import str2bool, get_env_variable, parse_descriptor_to_dict, mod_version_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

### Command line inputs ###
# the user shouldn't even see these, they're for the github action to call
parser = argparse.ArgumentParser()
parser.add_argument("versionType", type=str, choices=cao.possible_version_types, help="version type to bump")
parser.add_argument("versionStellaris", type=str, help="Stellaris version to support")
# argparse does not have a proper bool method, so custom implementation in module
parser.add_argument("useChangelog", type=str2bool, help="Whether to use changelog file")
parser.add_argument("modFolderName", type=str, help="Name of mod folder (and repository)") # this is set to just be the repo name, use ${{ github.event.repository.name }}
parser.add_argument("repoGithubpath", type=str, help="Mod repository Github path, username+repo_name") # used for constructing links - just use ${{ github.repository }}
args = parser.parse_args()

if cao.debug_level >= 1:
    print("- Inputs -")
    print("versionType:", args.versionType)
    print("versionStellaris:", args.versionStellaris)
    print("useChangelog:", args.useChangelog)
    print("modFolderName:", args.modFolderName)
    print("repoGithubpath:", args.repoGithubpath)

### File paths ###
if cao.debug_level >= 1:
    print("\n- Paths -")
    print("Working directory for Python script:", Path.cwd())
    print("Path to mod files:", cao.mod_github_folder_path)
    print("Descriptor file location:", cao.descriptor_file_path)

### File parsing ###
# grab descriptor and break it down into a python dict
descriptor_dict = parse_descriptor_to_dict(cao.descriptor_file_path)

if cao.debug_level >= 2:
    print("- Extracted descriptor dictionary: -")
    for key, item in descriptor_dict.items():
        print(f"{key}: {item}")

### Processing ###
## Mod version
# takes the mod version str and increments the selected bit according to semantic versioning
# also returns a dict with the split up semantic pieces (usually major version, minor version, and patch version)
current_semantic_versions, updated_mod_version = increment_mod_version(descriptor_dict["version"], args.versionType, possible_version_types=cao.possible_version_types)

# and we make a version suitable for a github release tag - this should be v1.2.3
# user provided/paradox mod versioning supports a space (v 1.2.3) or completely omitting the v
# this is not valid for github so need to re-make a github tag style version
github_release_tag = "v" + ".".join(current_semantic_versions.values())

# make yet another version of version number, this one with underscores so it's valid as a filename
# v1.2.3 -> v1_2_3
for_filename_mod_version = "v" + "_".join(current_semantic_versions.values())

if cao.debug_level >= 2:
    print(f"Broken down version dict: {current_semantic_versions}")
    print(f"Post-bump mod version: {updated_mod_version}")
    print(f"Github release tag to use: {github_release_tag}")

## Supported Stellaris version
# for display in descriptions, change any asterisks to x
# and remove the initial v too (matter of preference tbh)
supported_stellaris_version_display = args.versionStellaris.replace("*", "x")
supported_stellaris_version_display = supported_stellaris_version_display.replace("v", "")
# NOTE: does not support custom display rules

# for use in a mod name, like `Mod Name (4.0)`, Gigastructures does this
# rely on default values for function, Stellaris version format is fixed beyond the user
# catch errors and return a more helpful message
try:
    current_semantic_versions, using_v_prefix, using_v_with_space_prefix = mod_version_to_dict(args.versionStellaris)
except ValueError:
    raise ValueError(f"Input Stellaris version must be formatted correctly, should be of type \"v1.2.3\", got {args.versionStellaris}")
stellaris_major_minor_version = f"{current_semantic_versions['Major']}.{current_semantic_versions['Minor']}"
supported_stellaris_version_in_name = f"({stellaris_major_minor_version})" # put in parenthesis
supported_stellaris_version_in_name = supported_stellaris_version_display.replace("v", "") # just in case

if cao.debug_level >= 2:
    print(f"Input supported Stellaris version: {args.versionStellaris}")
    print(f"For display: {supported_stellaris_version_display}")
    print(f"For mod name: {supported_stellaris_version_in_name}")

## Processing for descriptor file
# make path manually, should always prefer relative path
# don't want to leak a username with an absolute path
# but allow override to manually specify a path setup
if cao.descriptor_override_path is None:
    generated_path = f"mod/{cao.mod_repo_name}/{cao.mod_folder_name}"
else:
    generated_path = cao.descriptor_override_path

# check if override has a different stellaris version to support for descriptor
# will use the supported version for other purposes regardless
if cao.descriptor_override_supported_version is None:
    generated_supported_version = args.versionStellaris
else:
    generated_supported_version = cao.descriptor_override_supported_version

# update dict, these are always generated
descriptor_dict["version"] = updated_mod_version
descriptor_dict["path"] = generated_path
descriptor_dict["supported_version"] = generated_supported_version

# check if any other parameters had requested overrides
if cao.override_enabled:
    # check if we want another name - make supported stellaris version available
    # useful for say gigastructures' mod naming convention
    if cao.descriptor_override_name is not None:
        descriptor_dict["name"] = cao.descriptor_override_name.format(stellaris_version=supported_stellaris_version_in_name)
    
    # misc overrides
    if cao.descriptor_override_tags is not None:
        descriptor_dict["tags"] = cao.descriptor_override_tags
    if cao.descriptor_override_picture is not None:
        descriptor_dict["picture"] = cao.descriptor_override_picture
    if cao.descriptor_override_remote_file_id is not None:
        descriptor_dict["remote_file_id"] = cao.descriptor_override_remote_file_id

if cao.debug_level >= 2:
    print("- Updated descriptor dictionary: -")
    for key, item in descriptor_dict.items():
        print(f"{key}: {item}")

## Finish up with descriptor file
create_descriptor_file(descriptor_dict, cao.descriptor_file_path)
if cao.debug_level >= 2:
    print("- Descriptor written to file -")

### Update workshop description, if it exists ###
if cao.workshop_description_file_path.exists():
    # format of line with version number can be overriden 
    # NOTE: must have two regex group references on the side of the version number to replace
    # by default look for "Supports Stellaris version: 1.2.x" with version number bolded in steam BBcode
    new_workshop_desc_version = f"\\g<1>{supported_stellaris_version_display}\\g<2>"

    workshop_file_string = search_and_replace_in_file(cao.workshop_description_file_path, cao.workshop_desc_version_pattern, new_workshop_desc_version)

### Similarly update readme file, if it exists ###
if cao.readme_file_path.exists():
    # format to look for can be overriden - must have two regex group references on the side of the version number to replace
    # by default look for "Supports Stellaris version: `1.2.x`" with version number using code embed in markdown
    new_readme_version = f"\\g<1>{supported_stellaris_version_display}\\g<2>"

    readme_file_string = search_and_replace_in_file(cao.readme_file_path, cao.readme_version_pattern, new_readme_version)

### Update any loc files as requested ###
# is skipped if there is nothing
if cao.loc_files_list:
    for file_name in cao.loc_files_list:
        loc_file_path = (cao.mod_files_folder_path / file_name).resolve()
        
        # change mod version in a loc file for access in-game
        # inserts requested specific key into a generic search pattern for loc files
        version_loc_key_pattern = cao.loc_key_pattern.fo*rmat(cao.version_loc_key)
        # uses regex groups in `version_loc_key_pattern`
        new_version_loc_key = f"\\g<1>{updated_mod_version}\\g<2>"

        # potential other keys to change to go here

        loc_file_string = search_and_replace_in_file(loc_file_path, version_loc_key_pattern, new_version_loc_key)

### Process changelog ###
# uses regex groups in `template_insert_version_pattern`
new_template_insert_version = f"\\g<1>\\g<2>{supported_stellaris_version_display}\\g<3>"

# user specified to use changelog
if args.useChangelog:
    if not cao.changelog_file_path.exists():
        raise ValueError(f"Requested adding changelog to release notes, but no file {cao.changelog_file_name} was provided in repository")

    # handle link
    github_release_link = cao.github_release_link_pattern.format(args.repoGithubpath, github_release_tag)
    
    # process changelog with release link and version number
    # regex groups must match `changelog_search_pattern`
    if not cao.add_changelog_WIP_entry:
        # normal replace
        changelog_replace = f"\\g<1>\\g<2>[\\g<3>{updated_mod_version}\\g<4>]({github_release_link})\\g<5>\\g<6>\\g<7>"
    else:
        # add an extra WIP entry to be filled when making the next version of the mod
        WIP_entry = f"\\g<1>\\g<2>\\g<3>WIP\\g<4>\\g<5>- Newest changes\n\\g<7>\n\n"
        changelog_replace = WIP_entry + f"\\g<1>\\g<2>[\\g<3>{updated_mod_version}\\g<4>]({github_release_link})\\g<5>\\g<6>\\g<7>"
    
    # this replaces the WIP on the latest change entry in the original changelog file from the mod repo
    # and also turns it into a link that will lead to the release we will be creating
    original_changelog_file_string, new_changelog_file_string = search_and_replace_in_file(cao.changelog_file_path, cao.changelog_search_pattern, changelog_replace, return_old_str=True)
    
    # fill in template to make a file to bundle as release notes
    # grab the changelog entry from the original file, change the WIP to version number, then fill in template
    # note use of extracted changelog string, the source file has been updated already
    if match := re.search(cao.changelog_search_pattern, original_changelog_file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL):
        # fills in string with groups retrieved from regex search, in order
        release_changelog_entry = f"{match[1]}{match[2]}{match[3]}{updated_mod_version}{match[4]}{match[5]}{match[6]}{match[7]}"
        
        if cao.debug_level >= 2:
            print("- Finished changelog entry going into release notes: -")
            print(release_changelog_entry)
            print("- Name and path of output file with release notes: -")
            print(cao.generated_release_notes_file_path)
    
    template_file_string = generate_with_template_file(cao.release_note_template_file_path, cao.generated_release_notes_file_path, [cao.template_insert_version_pattern, cao.template_search_pattern], [new_template_insert_version, release_changelog_entry], skip_regex_replace=False)

# user is not using changelogs
else:
    # check if special fixed template requested
    if not cao.release_note_template_overriden:
        # it wasn't, rename the template object to use the default
        release_note_template_file_path = cao.release_note_template_no_changelog_file_path
        
        # use auto-generated release notes here instead? somehow need to pass change in behaviour to github release command in workflow later

    else:
        # use user template
        release_note_template_file_path = cao.release_note_template_file_path

    # no change notes, uses template directly
    # dynamically change the supported stellaris version though
    template_file_string = generate_with_template_file(release_note_template_file_path, cao.generated_release_notes_file_path, cao.template_insert_version_pattern, new_template_insert_version, skip_regex_replace=False)

### Preparing environment variables to help create release ###
env_file_path = get_env_variable('GITHUB_ENV', None, debug_level=cao.debug_level)

# save path of generated changelog file
with open(env_file_path, "a") as envfile: # type: ignore - false error from parsing a str filename which works fine when the file exists in the actual github env
    print(f'{cao.github_env_releasenotesfile_name}={cao.generated_release_notes_file_path}', file=envfile)
    
# create title from mod name + the release tag - used for commit message and release title
release_title = f"{descriptor_dict['name']} {github_release_tag}"
# release zipfile name must be acceptable format
release_zipfile_name = f"{cao.mod_folder_name}_{for_filename_mod_version}.zip"
# make useful environment variables
with open(env_file_path, "a") as envfile: # type: ignore - false error from parsing a str filename which works fine when the file exists in the actual github env
    print(f'{cao.github_env_releasetitle_name}={release_title}', file=envfile)
    print(f'{cao.github_env_modreleasetag_name}={github_release_tag}', file=envfile)
    print(f'{cao.github_env_descriptorfile_name}={cao.descriptor_file_name}', file=envfile)
    print(f'{cao.github_env_releasezipfile_name}={release_zipfile_name}', file=envfile)

# release handled by github CLI commands in shell script
