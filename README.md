# stellaris_mod_deploy_action

![Stellaris Mod Deploy Action Status](https://github.com/aerolfos/stellaris_mod_deploy_action/actions/workflows/updateStellarisMod.yml/badge.svg)
[![GitHub Release Badge](https://img.shields.io/github/v/release/aerolfos/stellaris_mod_deploy_action?logo=github&style=flat)](https://github.com/Aerolfos/stellaris_mod_deploy_action/releases/latest)
[![Repository License](https://img.shields.io/github/license/aerolfos/stellaris_mod_deploy_action?style=flat&color=brightgreen)](LICENSE)
<!---[![Discord](https://img.shields.io/discord/739835273969664050?style=flat&label=Discord&logo=discord&logoColor=white&color=7289DA)](https://discord.com/invite/xUrG9wh)--->


This is a custom tool to aid in updating Stellaris mods. It only makes sense to use this tool if you structure mods similarly, see below under usage.

This tool uses the [Github action](https://github.com/features/actions) functionality to trigger a Python script which bumps version numbers and supported Stellaris version, and also creates a Github release for the mod.

## Usage
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

## In practice
https://github.com/Aerolfos/stellaris_mod_deploy_action/blob/main/.github/workflows/example.yml

`.../Paradox Interactive/Stellaris/mod/mod_name`

https://docs.github.com/en/actions/about-github-actions/understanding-github-actions

![action run button UI](https://github.com/user-attachments/assets/da909f08-7a52-4e7f-b7f8-eb74b546b80c)

![action run button UI](https://github.com/user-attachments/assets/da909f08-7a52-4e7f-b7f8-eb74b546b80c)

`version="v1.2.0"`

`supported_version="v3.*.*"`

https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning

https://github.com/Aerolfos/stellaris_mod_deploy_action/wiki/Tool-setup

https://github.com/Aerolfos/dubstep_launchers/blob/main/CHANGELOG.md

![workflow dispatch trigger UI](https://github.com/user-attachments/assets/61fe3527-5eca-4160-9520-1383b2203a6e)

![actions name in UI](https://github.com/user-attachments/assets/c96d32a7-12ef-4b92-b212-9167a3ba0361)

![github actions button UI position](https://github.com/user-attachments/assets/55c539cf-c86b-4a5f-aabf-1b1f675c5425)





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
