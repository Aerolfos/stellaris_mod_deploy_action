import argparse
import re
from methods.input_methods import str2bool, extract_file_data, replace_file_data, extract_and_replace_mod_version

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
descriptor_file_object = "descriptor.mod"

# regex matches must be unique, if they aren't the solution is to clean up the file first

# match the paradox descriptor version line, should be of form version="1.2.3", wildcards * are allowed
# must create a regex group where the version is read to
regex_version_pattern = r"^version=\"((?:(?:\d{1,3}|\*)\.){2}(?:\d{1,3}|\*))\"" # yeah regex be like that

# match the supported stellaris version, must be version="1.2.3", wildcard * in any position are allowed
regex_supportedstellaris_pattern = r"^supported_version=\"((?:(?:\d{1,3}|\*)\.){2}(?:\d{1,3}|\*))\""

# if the version="" and supported_version="" syntax ever needs to be changed it's hardcoded in the functions when updating string

descriptor_string = extract_file_data(descriptor_file_object)

updated_mod_version = extract_and_replace_mod_version(descriptor_string, regex_version_pattern, args.versionType)

replace_file_data(descriptor_file_object, descriptor_string)

