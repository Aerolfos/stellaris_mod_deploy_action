# stellaris_mod_deploy_action

![Testing Status](https://github.com/aerolfos/stellaris_mod_deploy_action/actions/workflows/Testing.yml/badge.svg)
[![GitHub Release Badge](https://img.shields.io/github/v/release/aerolfos/stellaris_mod_deploy_action?logo=github&style=flat)](https://github.com/Aerolfos/stellaris_mod_deploy_action/releases/latest)
[![Repository License](https://img.shields.io/github/license/aerolfos/stellaris_mod_deploy_action?style=flat&color=brightgreen)](LICENSE)
<!---[![Discord](https://img.shields.io/discord/739835273969664050?style=flat&label=Discord&logo=discord&logoColor=white&color=7289DA)](https://discord.com/invite/xUrG9wh)--->


This is a custom tool to aid in updating Stellaris mods. It only makes sense to use this tool if you structure mods similarly, see below under setup.

Target audience is developers familiar with GitHub already, who want to use GitHub both for version control and to make their mods more accessible to the open source community.

This tool uses the [GitHub actions](https://github.com/features/actions) functionality to trigger a Python script which bumps version numbers, changes supported Stellaris version in various places, and then creates a Github release for the mod.

Also integrates [TTFTCUTS' localisation processing action](https://github.com/TTFTCUTS/Stellaris-Loc-Action) as an optional step that can be triggered, which will propagate loc entries from English to other languages before generating a release.

Basically, this tool deals with parity issues by consolidating input needed for a mod update to a single place. Thus it automates away having to fill in metadata in a bunch of different places, one of which will inevitably be forgotten. [Here's an example of changes made by the script for a mod update](https://github.com/Aerolfos/dubstep_launchers/commit/848613fd8d76b55532b5087a33e3b9dfb22106e6).

## Usage
After setup, in the Github repository for a mod with an update to be released, go to the actions tab in the UI.

![github actions button UI position](https://github.com/user-attachments/assets/55c539cf-c86b-4a5f-aabf-1b1f675c5425)

Select the correct workflow in the left sidebar, by default it should be called `Deploy Stellaris mod update`.

![actions name in UI](https://github.com/user-attachments/assets/c96d32a7-12ef-4b92-b212-9167a3ba0361)

Trigger the workflow from the button, and fill in the necessary inputs in the dropdown.

![workflow dispatch trigger UI](https://github.com/user-attachments/assets/61fe3527-5eca-4160-9520-1383b2203a6e)

![action run button UI](https://github.com/user-attachments/assets/da909f08-7a52-4e7f-b7f8-eb74b546b80c)

If using the changelog feature, do not forget to double check that your changelog file (default, `CHANGELOG.md`) has the appropriate entries for the update ([example of a changelog](https://github.com/Aerolfos/nod_voice_advisor/blob/main/CHANGELOG.md)). I like to write these as I'm working on an update, both as a todo-list and a reminder of what I finished already, like mentioned in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/#effort). The most recent changelog entries should be under `WIP` (insert picture here).

The workflow will take a few seconds to start (reload the actions page to see it), and then finish within a minute or less. Once a workflow shows success in the UI, there should be a new commit to the repository ([example](https://github.com/Aerolfos/dubstep_launchers/commit/848613fd8d76b55532b5087a33e3b9dfb22106e6)), and a new release ([example](https://github.com/Aerolfos/dubstep_launchers/releases/tag/v1.2.1)).

Remember to pull these changes to your local repository, and then upload the mod to the steam workshop.


WIP: How to use and structure mod setup

https://github.com/Aerolfos/stellaris_mod_deploy_action/wiki/Mod-file-locations

`Paradox Interactive/Stellaris/mod/`

https://stellaris.paradoxwikis.com/Mods

`Paradox Interactive/Stellaris/mod/`

https://stellaris.paradoxwikis.com/Modding#Mod_management

`.../Paradox Interactive/Stellaris/mod/mod_name`

`mod_name`

https://github.com/Aerolfos/dubstep_launchers

https://github.com/Aerolfos/dubstep_launchers/blob/main/dubstep_launchers/descriptor.mod

https://github.com/Aerolfos/stellaris_mod_deploy_action/wiki/Expected-mod-structure

## Setup
https://github.com/Aerolfos/stellaris_mod_deploy_action/blob/main/.github/workflows/example.yml

`.../Paradox Interactive/Stellaris/mod/mod_name`

https://docs.github.com/en/actions/about-github-actions/understanding-github-actions

![action run button UI](https://github.com/user-attachments/assets/da909f08-7a52-4e7f-b7f8-eb74b546b80c)

`version="v1.2.0"`

`supported_version="v3.*.*"`

https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning

https://github.com/Aerolfos/stellaris_mod_deploy_action/wiki/Tool-setup

https://github.com/Aerolfos/dubstep_launchers/blob/main/CHANGELOG.md






## License
Code and documentation are licensed under [GNU GPL v3.0](LICENSE).

This project is meant to support creating Stellaris mods, which are subject to the [Paradox User Agreement](https://legal.paradoxplaza.com/eula).

    Copyright (c) 2024 Aerolfos

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Contributions
If you for some reason want to contribute, why not. Open a pull request.

