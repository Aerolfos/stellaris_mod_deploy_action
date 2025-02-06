## code based on https://github.com/m00nl1ght-dev/steam-workshop-deploy/ and https://github.com/game-ci/steam-deploy

### Imports ###
import os
from pathlib import Path
import subprocess
import base64
import sys
from methods.input_methods import str2bool, get_env_variable, run_command, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

### Settings ###
debug_level = 1

### Environment variables, paths ###
home_dir_path = Path(get_env_variable('HOME', '/home', debug_level=debug_level)).resolve()
steam_home_dir_path = get_env_variable('STEAM_HOME', home_dir_path / '.local/share/Steam', debug_level=debug_level)
root_path = get_env_variable('rootPath', '', debug_level=debug_level) # TODO
content_root = Path.cwd() / root_path # TODO
manifest_file_path = Path.cwd() / 'manifest.vdf'

app_id = get_env_variable('appID', '', debug_level=debug_level)
item_id = get_env_variable('itemID', '', debug_level=debug_level)
change_note = get_env_variable('changeNote', 'Test', debug_level=debug_level)
steam_username = get_env_variable('steam_username', '', debug_level=debug_level)
config_vdf_contents = get_env_variable('configVdf', '', debug_level=debug_level)

### Errors ###
if not app_id:
    raise ValueError("Steam app ID is missing or incomplete, must have a game to upload mod for")
#if not item_id:
#    raise ValueError("Published file ID is missing or incomplete, must have an already uploaded workshop object")
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
    "contentfolder" "{content_root}"
    "previewfile" "{content_root}/thumbnail.png"
    "changenote" "{change_note}"
}}
'''

# reference file
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

with open(manifest_file_path, 'w') as manifest_file_object:
    manifest_file_object.write(manifest_content)

if debug_level >= 1:
    print("Home contents:", os.listdir(home_dir_path))
    print("Steam home contents:", os.listdir(steam_home_dir_path))
    print(".steam/steam contents:", os.listdir(home_dir_path / ".steam/steam"))
    print(".steam/root contents:", os.listdir(home_dir_path / ".steam/root"))

    print("Manifest:")
    print(manifest_content)

os.makedirs(steam_home_dir_path / 'config', exist_ok=True)

decoded_config_vdf = base64.b64decode(config_vdf_contents)
config_file_path = steam_home_dir_path / 'config' / 'config.vdf'
with open(config_file_path, 'wb') as config_file_object:
    config_file_object.write(decoded_config_vdf)
os.chmod(config_file_path, 0o777)

if debug_level >= 1:
    print(f"{config_file_path=}")
    print("Steam/config contents:", os.listdir(steam_home_dir_path / 'config'))

# test login
print("test login")
command = f'steamcmd +login "{steam_username}" +quit'
if run_command(command):
    print("Successful login")
else:
    print("FAILED login")
    subprocess.run("ls -alh", shell=True)
    subprocess.run(f"ls -alh {root_path} || true", shell=True)
    subprocess.run(f"ls -Ralph {steam_home_dir_path / 'logs'}", shell=True)
    sys.exit(1)

# upload the item
print("deliberate halt")
sys.exit(0)

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
