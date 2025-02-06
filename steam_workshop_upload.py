### Imports ###
import os
from pathlib import Path
import subprocess
import base64
import sys
from methods.input_methods import str2bool, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

debug_level = 1

# helper to get environment variables
def get_env_variable(env_var_name, default=None):
    """Simple getenv wrapper with debug print"""
    env_var = os.getenv(env_var_name, default)
    if debug_level >= 1:
        print(f"{env_var_name}={env_var}")
    return env_var

home_dir_path = Path(get_env_variable('HOME', '/home')).resolve()
steam_home_dir_path = get_env_variable('STEAM_HOME', home_dir_path / '.local/share/Steam')
root_path = get_env_variable('rootPath', '') # TODO
content_root = Path.cwd() / root_path # TODO
manifest_file_path = Path.cwd() / 'manifest.vdf'

app_id = get_env_variable('appID', '')
item_id = get_env_variable('itemID', '')
change_note = get_env_variable('changeNote', 'Test')
steam_username = get_env_variable('steam_username', '')
config_vdf_contents = get_env_variable('configVdf', '')

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

print("Manifest:")
print(manifest_content)

if debug_level >= 1:
    print("Home contents:", os.listdir(home_dir_path))
    print("Steam home contents:", os.listdir(steam_home_dir_path))
    print(".steam/steam contents:", os.listdir(home_dir_path / ".steam/steam"))
    print(".steam/root contents:", os.listdir(home_dir_path / ".steam/root"))

# function to run shell commands, for error handling
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as err:
        print(err)
        return False

# check SteamGuard authentication
if not config_vdf_contents:
    print("Config VDF input is missing or incomplete! Cannot proceed.")
    sys.exit(1)

os.makedirs(steam_home_dir_path / 'config', exist_ok=True)

decoded_config_vdf = base64.b64decode(config_vdf_contents)
config_file_path = steam_home_dir_path / 'config' / 'config.vdf'
with open(config_file_path, 'wb') as config_file_object:
    config_file_object.write(decoded_config_vdf)
os.chmod(config_file_path, 0o777)

# test
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
