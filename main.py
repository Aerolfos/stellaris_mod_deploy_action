import argparse
import re
from pathlib import Path
from methods.input_methods import str2bool, parse_descriptor_to_dict, increment_mod_version

# handle command line inputs
# the user shouldn't even see these, they're for the github action to call
parser = argparse.ArgumentParser()
possible_version_types = ["Major", "Minor", "Patch"]
parser.add_argument("versionType", type=str, choices=possible_version_types, help="version type to bump")
parser.add_argument("versionStellaris", type=str, help="Stellaris version to support")
# argparse does not have a proper bool method, so custom implementation in module
parser.add_argument("useChangelog", type=str2bool, help="Whether to use changelog file")
parser.add_argument("modfolderName", type=str, help="Name of mod folder (and repository)") # this is set to just be the repo name
args = parser.parse_args()

print("- init -")
print("versionType:", args.versionType)
print("versionStellaris:", args.versionStellaris)
print("useChangelog:", args.useChangelog)
print("modfolderName:", args.modfolderName)

# path and name for the descriptor file
descriptor_file_name = "descriptor.mod"
user_profile_path = Path.home()
descriptor_file_object = user_profile_path / "Documents" / args.modfolderName / descriptor_file_name
print(descriptor_file_object)

# grab descriptor and break it down into a python dict
descriptor_dict = parse_descriptor_to_dict(descriptor_file_object)

print("- Extracted dictionary: -")
for key, item in descriptor_dict.items():
    print(f"{key}: {item}")

# takes the mod version str and increments the selected bit according to semantic versioning
# also returns a dict with the split up semantic pieces (usually major version, minor version, and patch version)
current_semantic_versions, updated_mod_version = increment_mod_version(descriptor_dict["version"], args.versionType, possible_version_types=possible_version_types)
print(current_semantic_versions)
print(updated_mod_version)

# update dict
descriptor_dict["version"] = updated_mod_version
descriptor_dict["supported_version"] = args.versionStellaris

print("- Updated dictionary: -")
for key, item in descriptor_dict.items():
    print(f"{key}: {item}")

#replace_file_data(descriptor_file_object, descriptor_file_string)

