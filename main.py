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
args = parser.parse_args()

print("init")
print(args)
print("useChangelog:", args.useChangelog)

# match the paradox descriptor version line, should be of form version="1.2.3", wildcards * are allowed
regex_version_pattern = r"version=\"((?:(?:\d{1,3}|\*)\.){2}(?:\d{1,3}|\*))\"" # yeah regex be like that

with open("descriptor", "r", encoding="utf-8") as f:
    descriptor_data = f.read()

with open("descriptor", "w", encoding="utf-8") as f:
    f.write(descriptor_data)

def replace(file, pattern, subst):
    # Read contents from file as a single string
    file_handle = open(file, 'r', encoding="utf-8")
    file_string = file_handle.read()
    file_handle.close()

    if match := re.search(pattern, text, re.IGNORECASE):
        mod_version = match.group(1)
    # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
    file_string = (re.sub(pattern, subst, file_string))

    # Write contents to file.
    # Using mode 'w' truncates the file.
    file_handle = open(file, 'w', encoding="utf-8")
    file_handle.write(file_string)
    file_handle.close()
