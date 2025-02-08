### Imports ###
import os
from pathlib import Path
import subprocess
import base64
import sys
from methods.input_methods import str2bool, get_env_variable, run_command, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

### Settings ###
# debug level 0 prints nothing, 1 inputs and paths, 2 prints information about parsing and processing
debug_level = 1
# 0, 1, or 2

# whether to add a new WIP entry to changelogs for filling in
default_add_changelog_WIP_entry = True

### Constants ###
# environment variable names (passed to github action environment)
github_env_modreleasetag_name = "MOD_RELEASE_TAG"
github_env_releasetitle_name = "MOD_RELEASE_TITLE"
github_env_releasenotesfile_name = "MOD_RELEASENOTES_FILE"
github_env_descriptorfile_name = "MOD_DESCRIPTOR_FILE"
github_env_releasezipfile_name = "MOD_RELEASE_ZIP_FILE"


