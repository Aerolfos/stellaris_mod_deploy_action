### Imports ###
import os
import subprocess
import base64
import sys

# get environment variables
steam_home = os.getenv('STEAM_HOME', os.path.join(os.getenv('HOME'), 'Steam'))
root_path = os.getenv('rootPath', '')
content_root = os.path.join(os.getcwd(), root_path)
manifest_path = os.path.join(os.getcwd(), 'manifest.vdf')

app_id = os.getenv('appId', '')
item_id = os.getenv('itemId', '')
change_note = os.getenv('changeNote', '')
steam_totp = os.getenv('steam_totp', '')
steam_username = os.getenv('steam_username', '')
steam_password = os.getenv('steam_password', '')
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

with open(manifest_path, 'w') as manifest_file:
    manifest_file.write(manifest_content)

print("Manifest:")
print(manifest_content)

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
    command = f'steamcmd +set_steam_guard_code "{steam_totp}" +login "{steam_username}" "{steam_password}" +quit'
    if run_command(command):
        print("Successful login")
    else:
        print("FAILED login")
        sys.exit(1)
else:
    if not config_vdf:
        print("Config VDF input is missing or incomplete! Cannot proceed.")
        sys.exit(1)

    steam_totp = "INVALID"

    os.makedirs(os.path.join(steam_home, 'config'), exist_ok=True)

    config_path = os.path.join(steam_home, 'config', 'config.vdf')
    with open(config_path, 'wb') as config_file:
        config_file.write(base64.b64decode(config_vdf))
    os.chmod(config_path, 0o777)

    command = f'steamcmd +login "{steam_username}" +quit'
    if run_command(command):
        print("Successful login")
    else:
        print("FAILED login")
        sys.exit(1)

# upload the item
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
