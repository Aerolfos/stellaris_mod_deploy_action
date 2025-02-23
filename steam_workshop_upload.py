"""
code based on https://github.com/m00nl1ght-dev/steam-workshop-deploy/ and https://github.com/game-ci/steam-deploy

requires a steam "build" account added as a contributor to your workshop item
account will be used with steamcmd
"""

### Imports ###
import base64
import os
import subprocess
from pathlib import Path

import constants_and_overrides as cao
from methods.input_methods import (
    get_env_variable,
    parse_descriptor_to_dict,
    str2bool,
)

timeout_time = 60 # s

### Environment variables, paths ###
# secrets
steam_username = get_env_variable("steam_username", None, debug_level=cao.debug_level)
config_vdf_contents = get_env_variable("configVdf", None, debug_level=cao.debug_level)
# normal env variables
app_id = get_env_variable("appID", None, debug_level=cao.debug_level)
input_stellaris_version = get_env_variable("versionStellaris", None, debug_level=cao.debug_level)
use_changelog = str2bool(get_env_variable("useChangelog", "false", debug_level=cao.debug_level))

# TODO: change flow
change_note = "TEST deployment from Github"

# dependent on docker container image used to set up steamcmd
home_dir_path: Path = Path(get_env_variable("HOME", "/home", debug_level=cao.debug_level)).resolve()
steam_home_dir_path: Path = Path(
    get_env_variable("STEAM_HOME", home_dir_path / ".local/share/Steam", debug_level=cao.debug_level),
)

### Errors ###
if not app_id:
    msg = "Steam app ID is missing or incomplete, must have a game to upload mod for"
    raise ValueError(msg)
# if not item_id:
#    raise ValueError("Published file ID is missing or incomplete, must have an already uploaded workshop object")
if not cao.mod_folder_name:
    msg = "Mod folder name is missing or incomplete, it should be Github repo name, how did you manage that?"
    raise ValueError(msg)
if not steam_username:
    msg = "Steam username is missing or incomplete, must have an account to upload with"
    raise ValueError(msg)
# check SteamGuard authentication
if not config_vdf_contents:
    msg = "Config VDF input file is missing or incomplete, must have configured account to upload with"
    raise ValueError(msg)

### Processing ###
# find information from mod files
descriptor_dict = parse_descriptor_to_dict(cao.descriptor_file_path)

if cao.debug_level == "DEBUG":
    print("- Extracted descriptor dictionary: -")
    for key, item in descriptor_dict.items():
        print(f"{key}: {item}")

try:
    item_id = descriptor_dict["remote_file_id"]
except KeyError as err:
    msg = "Published file ID is missing or incomplete, must use an already published workshop object with ID in descriptor"
    raise ValueError(msg) from err

try:
    mod_title = descriptor_dict["name"]
except KeyError as err:
    msg = "Mod name is missing or incomplete, must have name in descriptor"
    raise ValueError(msg) from err

if not cao.workshop_description_file_path.exists():
    msg = f"File with workshop description '{cao.workshop_description_file_name}' is missing, \
    must have one for workshop upload feature"
    raise ValueError(msg)
file_handle = Path.open(cao.workshop_description_file_path)
workshop_description_file_string = file_handle.read()
workshop_description_file_string = workshop_description_file_string.replace('"', '\"')  # noqa: Q004 deliberately escaping quotes
file_handle.close()

# TODO: actual change note

### Metadata ###
# make manifest file with metadata
manifest_content = f""""workshopitem"
{{
    "appid" "{app_id}"
    "publishedfileid" "{item_id}"
    "contentfolder" "{cao.mod_files_folder_path}"
    "previewfile" "{cao.mod_files_folder_path / "thumbnail.png"}"
    "title" "{mod_title}"
    "description" "{workshop_description_file_string}"
    "changenote" "{change_note}"
}}
"""

# reference file, stellaris
"""
"workshopitem"
{
    "appid"        "281990"
    "contentfolder"        "C:\\Users\\...\\mod_name"
    "previewfile"        "C:\\Users\\...\\mod_name\\thumbnail.png"
    "visibility"        "2"
    "title"        "Example mod uploaded using SteamCmd"
    "description"        "New description."
    "changenote"        "Initial Release."
}
"""

with Path.open(cao.manifest_file_path, "w") as manifest_file_object:
    manifest_file_object.write(manifest_content)

if cao.debug_level in ["INFO", "DEBUG"]:
    print("Home contents:", os.listdir(home_dir_path))
    print("Steam home contents:", os.listdir(steam_home_dir_path))
    print(".steam/steam contents:", os.listdir(home_dir_path / ".steam/steam"))
    print(".steam/root contents:", os.listdir(home_dir_path / ".steam/root"))

    print("- Manifest: -")
    print(manifest_content)

### Login ###
# write the login cache file to make login work
(steam_home_dir_path / "config").mkdir(exist_ok=True)
decoded_config_vdf = base64.b64decode(config_vdf_contents)
config_file_path = steam_home_dir_path / "config" / "config.vdf"
with Path.open(config_file_path, "wb") as config_file_object:
    config_file_object.write(decoded_config_vdf)
config_file_path.chmod(0o777)

if cao.debug_level in ["INFO", "DEBUG"]:
    print(f"{config_file_path=}")
    print("Steam/config contents:", os.listdir(steam_home_dir_path / "config"))


def steamcmd_run(command: str, timeout_time: int = 60) -> int:
    """
    Function to run steamcmd

    Only exists to avoid having to retype error handling twice. That's it.
    """
    try:
        output = subprocess.run(args=command, shell=True, check=True, timeout=timeout_time)
        print(output)

    except subprocess.TimeoutExpired as err:
        print(f"Error: {err}")
        print("Cached credentials likely invalid, in which case steamcmd falls back to interactive mode, breaking control flow")
        print(output)
        msg = "Timed out, cached credentials likely invalid, this makes steamcmd fall back to interactive mode\
              and break control flow"
        raise subprocess.CalledProcessError(msg) from err

    except subprocess.CalledProcessError as err:
        # In case of error, output logs
        print("Errors during upload:")
        print(err)

        log_dir_path = steam_home_dir_path / "logs"
        log_command = ["ls", "-Ralph", log_dir_path]
        output = subprocess.run(args=log_command, check=False)
        print(output)

        if log_dir_path.is_dir():
            for log_filename in os.listdir(log_dir_path):
                log_file_path = log_dir_path / log_filename
                with Path.open(log_file_path) as f:
                    print(f"######## {log_filename}")
                    print(f.read())

        msg = "Stemcmd failed during upload"
        raise subprocess.CalledProcessError(msg) from err

    # no raised errors
    else:
        return output.returncode


print("Testing login")
login_command = f'steamcmd +login "{steam_username}" +quit'
retcode = steamcmd_run(login_command, timeout_time)

### Upload item ###
upload_command = f'steamcmd +login "{steam_username}" +workshop_build_item "{cao.manifest_file_path}" +quit'
retcode = steamcmd_run(upload_command, timeout_time)

# Output the manifest path
# TODO: use github upload artifact to upload the manifest file for inspection
github_output = os.getenv("GITHUB_OUTPUT", None)
with Path.open(github_output, "a") as gh_output_file:
    gh_output_file.write(f"manifest={cao.manifest_file_path}\n")
