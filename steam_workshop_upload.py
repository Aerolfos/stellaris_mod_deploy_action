## code based on https://github.com/m00nl1ght-dev/steam-workshop-deploy/ and https://github.com/game-ci/steam-deploy
# requires a steam "build" account added as a contributor to your workshop item
# account will be used with steamcmd

### Imports ###
import os
from pathlib import Path
import subprocess
import base64
import sys

import constants_and_overrides as cao
from methods.input_methods import str2bool, get_env_variable, run_command, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

### Environment variables, paths ###
# secrets
steam_username = get_env_variable('steam_username', None, debug_level=cao.debug_level)
config_vdf_contents = get_env_variable('configVdf', None, debug_level=cao.debug_level)
# normal env variables
app_id = get_env_variable('appID', None, debug_level=cao.debug_level)
versionStellaris = get_env_variable('versionStellaris', None, debug_level=cao.debug_level)
useChangelog = get_env_variable('useChangelog', 'false', debug_level=cao.debug_level)

item_id = get_env_variable('itemID', None, debug_level=cao.debug_level) # TODO, change flow
change_note = "TEST deployment from Github"

# dependent on docker container image used to set up steamcmd
home_dir_path = Path(get_env_variable('HOME', '/home', debug_level=cao.debug_level)).resolve()
steam_home_dir_path = get_env_variable('STEAM_HOME', home_dir_path / '.local/share/Steam', debug_level=cao.debug_level)

### Errors ###
if not app_id:
    raise ValueError("Steam app ID is missing or incomplete, must have a game to upload mod for")
#if not item_id:
#    raise ValueError("Published file ID is missing or incomplete, must have an already uploaded workshop object")
if not cao.mod_folder_name:
    raise ValueError("Mod folder name is missing or incomplete, it should be Github repo name, how did you manage that?")
if not steam_username:
    raise ValueError("Steam username is missing or incomplete, must have an account to upload with")
# check SteamGuard authentication
if not config_vdf_contents:
    raise ValueError("Config VDF input file is missing or incomplete, must have configured account to upload with")

### Metadata ###
# make manifest file with metadata
manifest_content = f'''"workshopitem"
{{
    "appid" "{app_id}"
    "publishedfileid" "{item_id}"
    "contentfolder" "{cao.mod_files_folder_path}"
    "previewfile" "{cao.mod_files_folder_path}/thumbnail.png"
    "changenote" "{change_note}"
}}
'''

# reference file, stellaris
'''
"workshopitem"
{
    "appid"        "281990"
    "contentfolder"        "C:\\Users\\...\\my_awesome_mod"
    "previewfile"        "C:\\Users\\...\\my_awesome_mod\\thumbnail.png"
    "visibility"        "2"
    "title"        "My awesome mod uploaded using SteamCmd"
    "description"        "New description."
    "changenote"        "Initial Release."
}
'''

with open(cao.manifest_file_path, 'w') as manifest_file_object:
    manifest_file_object.write(manifest_content)

if cao.debug_level >= 1:
    print("Home contents:", os.listdir(home_dir_path))
    print("Steam home contents:", os.listdir(steam_home_dir_path))
    print(".steam/steam contents:", os.listdir(home_dir_path / ".steam/steam"))
    print(".steam/root contents:", os.listdir(home_dir_path / ".steam/root"))

    print("- Manifest: -")
    print(manifest_content)

### Login ###
os.makedirs(steam_home_dir_path / 'config', exist_ok=True)
decoded_config_vdf = base64.b64decode(config_vdf_contents)
config_file_path = steam_home_dir_path / 'config' / 'config.vdf'
with open(config_file_path, 'wb') as config_file_object:
    config_file_object.write(decoded_config_vdf)
os.chmod(config_file_path, 0o777)

if cao.debug_level >= 1:
    print(f"{config_file_path=}")
    print("Steam/config contents:", os.listdir(steam_home_dir_path / 'config'))

print("Testing login")
command = f'steamcmd +login "{steam_username}" +quit'
if run_command(command):
    print("Successful login")
else:
    print("FAILED login")
    subprocess.run("ls -alh", shell=True)
    subprocess.run(f"ls -alh {cao.mod_files_folder_path} || true", shell=True)
    subprocess.run(f"ls -Ralph {steam_home_dir_path / 'logs'}", shell=True)
    sys.exit(1)

# upload the item
print("deliberate halt")
sys.exit(0)

### Upload item ###
upload_command = f'steamcmd +login "{steam_username}" +workshop_build_item "{manifest_file_path}" +quit'
if run_command(upload_command):
    print("Successful upload")
else:
    # In case of error, output logs
    print("Errors during upload")
    subprocess.run("ls -alh", shell=True)
    subprocess.run(f"ls -alh {root_path} || true", shell=True)
    subprocess.run(f"ls -Ralph {steam_home_dir_path / 'logs'}", shell=True)

    log_dir_path = steam_home_dir_path / 'logs'
    if os.path.isdir(log_dir_path):
        for log_filename in os.listdir(log_dir_path):
            log_file_path = log_dir_path / log_filename
            with open(log_file_path) as f:
                print(f"######## {log_filename}")
                print(f.read())

    sys.exit(1)

# Output the manifest path
# TODO: use github upload artifact to upload the manifest file for inspection
github_output = os.getenv('GITHUB_OUTPUT', '')
with open(github_output, 'a') as gh_output_file:
    gh_output_file.write(f"manifest={manifest_file_path}\n")
