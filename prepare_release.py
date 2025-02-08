### Imports ###
import argparse
import os
import re
from pathlib import Path

from constants_and_overrides import debug_level, default_add_changelog_WIP_entry, github_env_modreleasetag_name, github_env_releasetitle_name, github_env_releasenotesfile_name, github_env_descriptorfile_name, github_env_releasezipfile_name
from methods.input_methods import str2bool, get_env_variable, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

### Defaults ###
# default search patterns
# loc_something:0 "something" - 0 code intentional since numbers other than 0 are generated or messed with by some tool, usually
loc_key_pattern = "(\\s{}:0\\s\").+?(\")" # use with .format(loc_key)
# "Supports Stellaris version: 1.2.x" with version number bolded in steam BBcode
default_workshop_desc_version_pattern = r"(Supports Stellaris version: \[b\]).+?(\[/b\])"
# "Supports Stellaris version: `1.2.x`" with version number using code embed in markdown
default_readme_version_pattern = r"(Supports Stellaris version: \`).+?(\`)"
# fill in with {username/repo_name} and {release-tag}
github_release_link_pattern = r"https://github.com/{}/releases/tag/{}"
# search pattern for extracting changelog - expects latest changes to be under "WIP"
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

# filenames
default_release_note_template_filename = "release_note_template.md"
default_release_note_template_no_changelog_filename = "release_note_template_no_changelog.md"
generated_release_notes_filename = "generated_release_notes.md"

### Command line inputs ###
# the user shouldn't even see these, they're for the github action to call
parser = argparse.ArgumentParser()
possible_version_types = ["Major", "Minor", "Patch"]
parser.add_argument("versionType", type=str, choices=possible_version_types, help="version type to bump")
parser.add_argument("versionStellaris", type=str, help="Stellaris version to support")
# argparse does not have a proper bool method, so custom implementation in module
parser.add_argument("useChangelog", type=str2bool, help="Whether to use changelog file")
parser.add_argument("modfolderName", type=str, help="Name of mod folder (and repository)") # this is set to just be the repo name, use ${{ github.event.repository.name }}
parser.add_argument("repoGithubpath", type=str, help="Mod repository Github path, username+repo_name") # used for constructing links - just use ${{ github.repository }}
args = parser.parse_args()

if debug_level >= 1:
    print("- Inputs -")
    print("versionType:", args.versionType)
    print("versionStellaris:", args.versionStellaris)
    print("useChangelog:", args.useChangelog)
    print("modfolderName:", args.modfolderName)
    print("repoGithubpath:", args.repoGithubpath)

### Overrides ###
# cwd is set to where the python file is, which should be next to the folder with the mod files from the originating mod repository
mod_github_folder_path = (Path.cwd() / f"../{args.modfolderName}").resolve()
# and the folder with the actual game mod files (nested one down from github)
mod_files_folder_path = mod_github_folder_path / args.modfolderName

if debug_level >= 1:
    print("\n- Paths -")
    print("Python script file path:", Path.cwd())
    print("Path to mod files:", mod_github_folder_path)

# do overrides immediately
# file for potential overrides
override_file_name = "OVERRIDE.txt"
override_file_path = mod_github_folder_path / override_file_name
# if there are overrides, we parse them - use same structure as a paradox descriptor because we have the parser already
override_enabled = False
override_dict = {}
if override_file_path.exists():
    override_enabled = True
    override_dict = parse_descriptor_to_dict(override_file_path)

# file names
try:
    descriptor_file_name = override_dict["descriptor_file_name_override"]
except KeyError:
    descriptor_file_name = "descriptor.mod"

try:
    workshop_description_file_name = override_dict["workshop_description_file_name_override"]
except KeyError:
    workshop_description_file_name = "workshop.txt"

try:
    readme_file_name = override_dict["readme_file_name_override"]
except KeyError:
    readme_file_name = "README.md"

try:
    changelog_file_name = override_dict["changelog_file_name_override"]
except KeyError:
    changelog_file_name = "CHANGELOG.md"

try:
    add_changelog_WIP_entry = override_dict["add_changelog_WIP_entry_override"]
except KeyError:
    add_changelog_WIP_entry = default_add_changelog_WIP_entry

# use flag to carry information on whether this override happened
release_note_template_overriden = False
try:
    release_note_template_filename = override_dict["release_note_template_filename_override"]
    release_note_template_overriden = True
except KeyError:
    release_note_template_filename = default_release_note_template_filename

### File paths ###
# make file paths
# descriptor is nested twice
descriptor_file_path = mod_files_folder_path / descriptor_file_name
if debug_level >= 1:
    print("Descriptor file location:", descriptor_file_path)
workshop_description_file_path = mod_github_folder_path / workshop_description_file_name
readme_file_path = mod_github_folder_path / readme_file_name
changelog_file_path = mod_github_folder_path / changelog_file_name
# default template file is generic and with the script
# but otherwise, check user provided one (which can only come from *their* repo)
if release_note_template_overriden:
    release_note_template_file_path = mod_github_folder_path / release_note_template_filename
else:
    release_note_template_file_path = Path.cwd() / release_note_template_filename
# no changelog version
default_release_note_template_no_changelog_file_path = Path.cwd() / default_release_note_template_no_changelog_filename
# not in the folder with the mod repo so this doesn't get comitted, it's a temp file
generated_release_notes_file_path = Path.cwd() / generated_release_notes_filename

### File parsing ###
# grab descriptor and break it down into a python dict
descriptor_dict = parse_descriptor_to_dict(descriptor_file_path)

if debug_level >= 2:
    print("- Extracted dictionary: -")
    for key, item in descriptor_dict.items():
        print(f"{key}: {item}")

    print("- Overrides: -")
    try:
        for key, item in override_dict.items():
            print(f"{key}: {item}")
    except:
        print("No overrides")

### Processing ###
# takes the mod version str and increments the selected bit according to semantic versioning
# also returns a dict with the split up semantic pieces (usually major version, minor version, and patch version)
current_semantic_versions, updated_mod_version = increment_mod_version(descriptor_dict["version"], args.versionType, possible_version_types=possible_version_types)
# and we make a version suitable for a github release tag - this should be v1.2.3
# because updated mod version supports a space (v 1.2.3) it's not valid for github so need to re-make it
github_release_tag = "v" + ".".join(current_semantic_versions.values())

# make yet another version of version number, this one with underscores so it's valid as a filename
# v1.2.3 -> v1_2_3
for_filename_mod_version = "v" + "_".join(current_semantic_versions.values())

if debug_level >= 2:
    print("Broken down version dict:", current_semantic_versions)
    print("Post-bump mod version:", updated_mod_version)
    print("Github release tag to use:", github_release_tag)

# make path manually, should always prefer relative path
# don't want to leak a username with an absolute path
# but allow override to manually specify a path setup
try:
    generated_path = override_dict["path_override"]
except KeyError:
    generated_path = f"mod/{args.modfolderName}/{args.modfolderName}"

# update dict
descriptor_dict["version"] = updated_mod_version
descriptor_dict["path"] = generated_path
if override_enabled:
    # check if override has a different stellaris version to support for descriptor
    # still want the normal version for updating description though
    try:
        descriptor_dict["supported_version"] = override_dict["supported_version_override"]
    except KeyError:
        descriptor_dict["supported_version"] = args.versionStellaris

    # check if we want another name - make supported stellaris version available
    # useful for say gigastructures' mod naming convention
    try:
        descriptor_dict["name"] = override_dict["name_override"].format(descriptor_dict["supported_version"])
    # else skip
    except KeyError:
        pass
else:
    descriptor_dict["supported_version"] = args.versionStellaris

if debug_level >= 2:
    print("- Updated descriptor dictionary: -")
    for key, item in descriptor_dict.items():
        print(f"{key}: {item}")

# for display, change any asterisks to x
# and remove the initial v too (matter of preference tbh)
supported_stellaris_version_display = args.versionStellaris.replace("*", "x")
supported_stellaris_version_display = supported_stellaris_version_display.replace("v", "")
if debug_level >= 2:
    print(f"{supported_stellaris_version_display=}")

### Update workshop description, if it exists ###
if workshop_description_file_path.exists():
    try:
        # format to look for can be overriden - must have two regex group references on the side of the version number to replace
        workshop_desc_version_pattern = override_dict["workshop_desc_version_pattern"]
    except KeyError:
        # by default look for "Supports Stellaris version: 1.2.x" with version number bolded in steam BBcode
        workshop_desc_version_pattern = default_workshop_desc_version_pattern
    
    # uses regex groups from above
    new_workshop_desc_version = f"\\g<1>{supported_stellaris_version_display}\\g<2>"

    workshop_file_string = search_and_replace_in_file(workshop_description_file_path, workshop_desc_version_pattern, new_workshop_desc_version)

### Similarly update readme file, if it exists ###
if readme_file_path.exists():
    try:
        # format to look for can be overriden - must have two regex group references on the side of the version number to replace
        readme_version_pattern = override_dict["readme_version_pattern"]
    except KeyError:
        # by default look for "Supports Stellaris version: `1.2.x`" with version number using code embed in markdown
        readme_version_pattern = default_readme_version_pattern
    
    # uses regex groups from above
    new_readme_version = f"\\g<1>{supported_stellaris_version_display}\\g<2>"

    readme_file_string = search_and_replace_in_file(readme_file_path, readme_version_pattern, new_readme_version)

### Update any loc files as requested ###
try: 
    loc_files_list = override_dict["extra_loc_files_to_update"]
    for file_name in loc_files_list:
        loc_file_path = (mod_files_folder_path / file_name).resolve()
        
        # change version in a loc file for access in-game
        version_loc_key = override_dict["version_loc_key"]
        version_loc_key_pattern = loc_key_pattern.format(version_loc_key)
        new_version_loc_key = f"\\g<1>{updated_mod_version}\\g<2>"

        # potential other keys to change to go here

        loc_file_string = search_and_replace_in_file(loc_file_path, version_loc_key_pattern, new_version_loc_key)

# if none then just skip
except KeyError:
    pass

### Process changelog ###
try:
    template_insert_version_pattern = override_dict["template_insert_version_pattern"]
except KeyError:
    # fallback to default
    template_insert_version_pattern = default_template_insert_version_pattern

# uses regex groups from above
new_template_insert_version = f"\\g<1>\\g<2>{supported_stellaris_version_display}\\g<3>"

if args.useChangelog:
    if not changelog_file_path.exists():
        raise ValueError(f"Requested adding changelog to release notes, but no file {changelog_file_name} was provided in repository")
    
    # changelog format to search for can be overriden - must have matching regex group references
    try:
        changelog_search_pattern = override_dict["changelog_search_pattern"]
    except KeyError:
        # fallback to default
        changelog_search_pattern = default_changelog_search_pattern

    try:
        template_search_pattern = override_dict["template_search_pattern"]
    except KeyError:
        # fallback to default
        template_search_pattern = default_template_search_pattern
    
    # uses regex groups from above, and makes a link
    github_release_link = github_release_link_pattern.format(args.repoGithubpath, github_release_tag)
    # straightforward replacing with link and version number
    if add_changelog_WIP_entry:
        # add an extra WIP entry to be filled when dev gets to it
        WIP_entry = f"\\g<1>\\g<2>\\g<3>WIP\\g<4>\\g<5>- Newest changes\n\\g<7>\n\n"
        changelog_replace = WIP_entry + f"\\g<1>\\g<2>[\\g<3>{updated_mod_version}\\g<4>]({github_release_link})\\g<5>\\g<6>\\g<7>"
    else:
        changelog_replace = f"\\g<1>\\g<2>[\\g<3>{updated_mod_version}\\g<4>]({github_release_link})\\g<5>\\g<6>\\g<7>"
    
    
    # this replaces the WIP on the latest change entry in the original changelog file from the mod repo
    # and also turns it into a link that will lead to the release we will be creating
    original_changelog_file_string, new_changelog_file_string = search_and_replace_in_file(changelog_file_path, changelog_search_pattern, changelog_replace, return_old_str=True)
    
    # grab the changelog entry from the original file, change the WIP to version number, then grab template file and fill it in
    if match := re.search(changelog_search_pattern, original_changelog_file_string, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL):
        # fills in string with groups retrieved from regex search, in order
        release_changelog_entry = f"{match[1]}{match[2]}{match[3]}{updated_mod_version}{match[4]}{match[5]}{match[6]}{match[7]}"
        
        if debug_level >= 2:
            print("- Finished changelog entry going into release notes: -")
            print(release_changelog_entry)
            print("- Name and path of output file with release notes: -")
            print(generated_release_notes_file_path)
    
    template_file_string = generate_with_template_file(release_note_template_file_path, generated_release_notes_file_path, [template_insert_version_pattern, template_search_pattern], [new_template_insert_version, release_changelog_entry])

    env_file_path = get_env_variable('GITHUB_ENV', None, debug_level=debug_level)
    with open(env_file_path, "a") as envfile: # type: ignore - false error from parsing a str filename which works fine when the file exists in the actual github env
        print(f'{github_env_releasenotesfile_name}={generated_release_notes_file_path}', file=envfile)

else:
    # check if special template requested
    if not release_note_template_overriden:
        # it wasn't, rename the template object so we actually use the bare version
        release_note_template_file_path = default_release_note_template_no_changelog_file_path
        # use auto-generated release notes here instead? somehow need to pass change in behaviour to github release command in workflow later

    # if special template was requested, it's already being passed, do nothing

    # no change notes, uses template directly
    # dynamically change the supported stellaris version though
    template_file_string = generate_with_template_file(release_note_template_file_path, generated_release_notes_file_path, template_insert_version_pattern, new_template_insert_version, skip_regex_replace=False)

    env_file_path = get_env_variable('GITHUB_ENV', None, debug_level=debug_level)
    with open(env_file_path, "a") as envfile: # type: ignore - false error from parsing a str filename which works fine when the file exists in the actual github env
        print(f'{github_env_releasenotesfile_name}={generated_release_notes_file_path}', file=envfile)
    

### Processing for just release object ###
# create title from mod name + the release tag - used for commit message and release title
release_title = f"{descriptor_dict['name']} {github_release_tag}"
# release zipfile name must be acceptable format
release_zipfile_name = f"{args.modfolderName}_{for_filename_mod_version}.zip"
# make useful environment variables
env_file_path = get_env_variable('GITHUB_ENV', None, debug_level=debug_level)
with open(env_file_path, "a") as envfile: # type: ignore - false error from parsing a str filename which works fine when the file exists in the actual github env
    print(f'{github_env_releasetitle_name}={release_title}', file=envfile)
    print(f'{github_env_modreleasetag_name}={github_release_tag}', file=envfile)
    print(f'{github_env_descriptorfile_name}={descriptor_file_name}', file=envfile)
    print(f'{github_env_releasezipfile_name}={release_zipfile_name}', file=envfile)

### Finish up with descriptor file ###
create_descriptor_file(descriptor_dict, descriptor_file_path)

