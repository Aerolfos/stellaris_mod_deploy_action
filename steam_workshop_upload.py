### Imports ###
import os
import subprocess
import base64
import sys

# get environment variables
steam_home = os.getenv('STEAM_HOME', os.path.join(os.getenv('HOME'), 'Steam'))
print(os.getenv('HOME'))
print(steam_home)
root_path = os.getenv('rootPath', '')
content_root = os.path.join(os.getcwd(), root_path)
manifest_path = os.path.join(os.getcwd(), 'manifest.vdf')

app_id = os.getenv('appID', '')
item_id = os.getenv('itemID', '')
change_note = os.getenv('changeNote', 'Test')
steam_username = os.getenv('steam_username', '')
config_vdf = os.getenv('configVdf', '')

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

with open(manifest_path, 'w') as manifest_file:
    manifest_file.write(manifest_content)

print("Manifest:")
print(manifest_content)

# test
os.listdir(os.getenv('HOME'))

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

os.makedirs(os.path.join(steam_home, 'config'), exist_ok=True)

config_path = os.path.join(steam_home, 'config', 'config.vdf')
with open(config_path, 'wb') as config_file:
    config_file.write(base64.b64decode(config_vdf))
os.chmod(config_path, 0o777)

# test
print(config_path)
os.listdir(os.path.join(steam_home, 'config'))

command = f'steamcmd +login "{steam_username}" +quit'
if run_command(command):
    print("Successful login")
else:
    print("FAILED login")
    sys.exit(1)

# upload the item
sys.exit(1)
upload_command = f'steamcmd +login "{steam_username}" +workshop_build_item "{manifest_path}" +quit'
if not run_command(upload_command):
    # In case of error, handle logs
    print("Errors during upload")
    subprocess.run("ls -alh", shell=True)
    subprocess.run(f"ls -alh {root_path} || true", shell=True)
    subprocess.run(f"ls -Ralph {os.path.join(steam_home, 'logs')}", shell=True)

    log_dir = os.path.join(steam_home, 'logs')
    if os.path.isdir(log_dir):
        for log_file in os.listdir(log_dir):
            log_path = os.path.join(log_dir, log_file)
            with open(log_path) as f:
                print(f"######## {log_file}")
                print(f.read())

    sys.exit(1)

# Output the manifest path
github_output = os.getenv('GITHUB_OUTPUT', '')
with open(github_output, 'a') as gh_output_file:
    gh_output_file.write(f"manifest={manifest_path}\n")
