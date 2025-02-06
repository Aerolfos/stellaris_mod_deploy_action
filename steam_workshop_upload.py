### Imports ###
import os
from pathlib import Path
import subprocess
import base64
import sys
from methods.input_methods import str2bool, parse_descriptor_to_dict, increment_mod_version, search_and_replace_in_file, create_descriptor_file, generate_with_template_file

debug_level = 1

# get environment variables
def get_env_variable(env_var_name, default=None):
    """Simple getenv wrapper with debug print"""
    env_var = os.getenv(env_var_name, default)
    if debug_level >= 1:
        print(f"{env_var_name}={env_var}")
    return env_var

home_dir = Path(get_env_variable('HOME', '/home')).resolve()
steam_home_dir = get_env_variable('STEAM_HOME', home_dir / '.steam')
root_path = get_env_variable('rootPath', '')
content_root = Path.cwd() / root_path
manifest_path_object = Path.cwd() / 'manifest.vdf'

app_id = get_env_variable('appID', '')
item_id = get_env_variable('itemID', '')
change_note = get_env_variable('changeNote', 'Test')
steam_username = get_env_variable('steam_username', '')
config_vdf = get_env_variable('configVdf', '')

# make manifest file with metadata
manifest_content = f'''"workshopitem"
{{
    "appid" "{app_id}"
    "publishedfileid" "{item_id}"
    "contentfolder" "{content_root}"
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

with open(manifest_path_object, 'w') as manifest_file:
    manifest_file.write(manifest_content)

print("Manifest:")
print(manifest_content)

# test
print("Home contents:", os.listdir(home_dir))
print("Home contents:", os.listdir(home_dir / ".steam"))

# function to run shell commands
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as err:
        print(err)
        return False

# handling SteamGuard authentication
if not config_vdf:
    print("Config VDF input is missing or incomplete! Cannot proceed.")
    sys.exit(1)

os.makedirs(steam_home_dir / 'config', exist_ok=True)

decoded_config_vdf = base64.b64decode(config_vdf)
config_path_object = steam_home_dir / 'config' / 'config.vdf'
with open(config_path_object, 'wb') as config_file:
    config_file.write(decoded_config_vdf)
os.chmod(config_path_object, 0o777)

# test
print(f"{config_path_object=}")
print("Steam/config contents:", os.listdir(steam_home_dir / 'config'))

# test login
print("test login")
command = f'steamcmd +login "{steam_username}" +quit'
if run_command(command):
    print("Successful login")
else:
    print("FAILED login")
    subprocess.run("ls -alh", shell=True)
    subprocess.run(f"ls -alh {root_path} || true", shell=True)
    subprocess.run(f"ls -Ralph {steam_home_dir / 'logs'}", shell=True)
    sys.exit(1)

# upload the item
print("deliberate halt")
sys.exit(1)
upload_command = f'steamcmd +login "{steam_username}" +workshop_build_item "{manifest_path_object}" +quit'
if run_command(upload_command):
    print("Successful upload")
else:
    # In case of error, output logs
    print("Errors during upload")
    subprocess.run("ls -alh", shell=True)
    subprocess.run(f"ls -alh {root_path} || true", shell=True)
    subprocess.run(f"ls -Ralph {steam_home_dir / 'logs'}", shell=True)

    log_dir = steam_home_dir / 'logs'
    #os.makedirs(log_dir, exist_ok=True)
    if os.path.isdir(log_dir):
        for log_file in os.listdir(log_dir):
            log_path = log_dir / log_file
            with open(log_path) as f:
                print(f"######## {log_file}")
                print(f.read())

    sys.exit(1)

# Output the manifest path
github_output = os.getenv('GITHUB_OUTPUT', '')
with open(github_output, 'a') as gh_output_file:
    gh_output_file.write(f"manifest={manifest_path_object}\n")
