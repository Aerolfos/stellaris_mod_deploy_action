import argparse
import re
from methods.input_methods import str2bool

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

# match the paradox descriptor version line, should be of form version="1.2.3", wildcards * are allowed
# must create a regex group where the version is read to
regex_version_pattern = r"version=\"((?:(?:\d{1,3}|\*)\.){2}(?:\d{1,3}|\*))\"" # yeah regex be like that

