### Imports ###
import argparse
import re
from pathlib import Path
from methods.input_methods import str2bool, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file

### Command line inputs ###
# the user shouldn't even see these, they're for the github action to call
parser = argparse.ArgumentParser()
possible_version_types = ["Major", "Minor", "Patch"]
parser.add_argument("versionType", type=str, choices=possible_version_types, help="version type to bump")
parser.add_argument("versionStellaris", type=str, help="Stellaris version to support")
# argparse does not have a proper bool method, so custom implementation in module
parser.add_argument("useChangelog", type=str2bool, help="Whether to use changelog file")
parser.add_argument("modfolderName", type=str, help="Name of mod folder (and repository)") # this is set to just be the repo name
args = parser.parse_args()

### Test ###
print("- init -")
print("versionType:", args.versionType)
print("versionStellaris:", args.versionStellaris)
print("useChangelog:", args.useChangelog)
print("modfolderName:", args.modfolderName)

### File paths ###
# get the path to where this python file is
working_folder = Path(__file__).resolve().parent
print(working_folder)

# do overrides immediately
# file for potential overrides
override_file_name = "OVERRIDE.txt"
override_file_object = working_folder / override_file_name
print(override_file_object)
# if there are overrides, we parse them - use same structure as a paradox descriptor because we have the parser already
override_enabled = False
override_dict = {}
if override_file_object.exists():
    override_enabled = True
    override_dict = parse_descriptor_to_dict(override_file_object)

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

# make file paths
descriptor_file_object = working_folder / descriptor_file_name
print(descriptor_file_object)
workshop_description_file_object = working_folder / workshop_description_file_name
readme_file_object = working_folder / readme_file_name

### File parsing ###
# grab descriptor and break it down into a python dict
descriptor_dict = parse_descriptor_to_dict(descriptor_file_object)

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
print(current_semantic_versions)
print(updated_mod_version)

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
else:
    descriptor_dict["supported_version"] = args.versionStellaris

print("- Updated dictionary: -")
for key, item in descriptor_dict.items():
    print(f"{key}: {item}")

# for display, change any asterisks to x
supported_stellaris_version_display = args.versionStellaris.replace("*", "x")
print(supported_stellaris_version_display)

### Update workshop description, if it exists ###
if workshop_description_file_object.exists():
    try:
        # format to look for can be overriden - must have two regex group references on the side of the version number to replace
        workshop_desc_version_pattern = override_dict["workshop_desc_version_pattern"]
    except KeyError:
        # by default look for "Supports Stellaris version: 1.2.x" with version number bolded in steam BBcode
        workshop_desc_version_pattern = r"(Supports Stellaris version: \[b\]).+(\[/b\])"
    
    # uses regex groups from above
    new_workshop_desc_version = f"\g<1>{supported_stellaris_version_display}\g<2>"

    search_and_replace_in_file(workshop_description_file_object, workshop_desc_version_pattern, new_workshop_desc_version)

### Similarly update readme file, if it exists ###
if readme_file_object.exists():
    try:
        # format to look for can be overriden - must have two regex group references on the side of the version number to replace
        readme_version_pattern = override_dict["readme_version_pattern"]
    except KeyError:
        # by default look for "Supports Stellaris version: `1.2.x`" with version number using code embed in markdown
        readme_version_pattern = r"(Supports Stellaris version: \`).+(\`)"
    
    # uses regex groups from above
    new_readme_version = f"\g<1>{supported_stellaris_version_display}\g<2>"

    search_and_replace_in_file(readme_file_object, readme_version_pattern, new_readme_version)

for loc_key in override_dict["loc_keys_to_match"]:
    override_loc_key_pattern = f"(\s{loc_key}:0\s\")(.+)(\")"


### File output ###
create_descriptor_file(descriptor_dict, descriptor_file_object)

