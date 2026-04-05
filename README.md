# stellaris_mod_deploy_action

![Testing Status](https://github.com/aerolfos/stellaris_mod_deploy_action/actions/workflows/Testing.yml/badge.svg)
[![GitHub Release Badge](https://img.shields.io/github/v/release/aerolfos/stellaris_mod_deploy_action?logo=github&style=flat)](https://github.com/Aerolfos/stellaris_mod_deploy_action/releases/latest)
[![Repository License](https://img.shields.io/github/license/aerolfos/stellaris_mod_deploy_action?style=flat&color=brightgreen)](LICENSE)
<!---[![Discord](https://img.shields.io/discord/739835273969664050?style=flat&label=Discord&logo=discord&logoColor=white&color=7289DA)](https://discord.com/invite/xUrG9wh)--->


This is a custom tool to aid in updating Stellaris mods. It only makes sense to use this tool if you structure mods similarly, see below under quick setup.

> [!NOTE]
> This tool has [the full documentation](https://aerolfos.github.io/stellaris_mod_deploy_action/) hosted on GitHub Pages, see that for details. This README is meant for a quick overview.

The target audience is Stellaris mod developers familiar with GitHub already, who want to use GitHub both for version control, and to make their mods more accessible to the open source community. Note that the deployment system should work for other Paradox strategy games, but was developed for Stellaris first.

This tool uses the [GitHub actions](https://github.com/features/actions) functionality to trigger a Python script which bumps version numbers, changes supported Stellaris version in various places, and then creates a GitHub release for the mod. It can also automate steam workshop uploads of this prepared release, but that feature is more complicated to set up. Check the [full documentation](https://aerolfos.github.io/stellaris_mod_deploy_action/Tool%20support/tool_setup/).

Also integrates [TTFTCUTS' localisation processing action](https://github.com/TTFTCUTS/Stellaris-Loc-Action) as an optional step that can be triggered, which will propagate loc entries from English to other languages before generating a release.

Basically, this tool deals with parity issues by consolidating input needed for a mod update to a single place. Thus, it automates away having to fill in metadata in a bunch of different places, one of which will inevitably be forgotten. [Here's an example of changes made by the script for a mod update](https://github.com/Aerolfos/dubstep_launchers/commit/848613fd8d76b55532b5087a33e3b9dfb22106e6).

## Usage
After [setup](https://aerolfos.github.io/stellaris_mod_deploy_action/Tool%20support/tool_setup/), first of all you need to update your mod and push the code to GitHub. If you tested your mod and no code changes were needed for compatibility, you can proceed to deployment right away *unless* you use the changelog feature. Then you will still need to write and push a change to the changelog file first.

Once you have an up-to-date configured GitHub repository for a mod with an update to be released, go to the actions tab in the UI.

![github actions button UI position](https://github.com/user-attachments/assets/55c539cf-c86b-4a5f-aabf-1b1f675c5425)

Select the correct workflow in the left sidebar, by default it should be called `Deploy Stellaris mod update`.

![actions name in UI](https://github.com/user-attachments/assets/c96d32a7-12ef-4b92-b212-9167a3ba0361)

Trigger the workflow from the button, and fill in the necessary inputs in the dropdown.

![workflow dispatch trigger UI](https://github.com/user-attachments/assets/61fe3527-5eca-4160-9520-1383b2203a6e)

![action run button UI](https://github.com/user-attachments/assets/da909f08-7a52-4e7f-b7f8-eb74b546b80c)

If using the changelog feature, do not forget to double-check that your changelog file (default, `CHANGELOG.md`) has the appropriate entries for the update ([example of a changelog](https://github.com/Aerolfos/nod_voice_advisor/blob/main/CHANGELOG.md)). I like to write these as I'm working on an update, both as a todo-list and a reminder of what I finished already, like mentioned in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/#effort). The most recent changelog entries should be under `WIP`. Before generating a release, a changelog should be similar to this image:

<img width="587" height="435" alt="[changelog with WIP section at top, filled out](https://github.com/Aerolfos/dubstep_launchers/blob/main/CHANGELOG.md)" src="https://github.com/user-attachments/assets/55f255df-3a4e-4c41-aef2-bf60d576905b" />


The workflow will take a few seconds to start (reload the actions page to see it), and then finish within a minute or less. Once a workflow shows success in the UI, there should be a new commit to the repository ([example](https://github.com/Aerolfos/dubstep_launchers/commit/848613fd8d76b55532b5087a33e3b9dfb22106e6)), and a new release ([example](https://github.com/Aerolfos/dubstep_launchers/releases/tag/v1.2.1)).

Remember to pull these changes to your local repository, and then upload the mod to the steam workshop.

If you set up automated workshop uploads properly, and added the workshop upload job to the main deployment workflow, the workshop upload should proceed on its own right after the GitHub release has finished. Note that if it's been a while since your last upload, the build account credentials might have expired and will need refreshing. In this case, you should use a separate workflow that only performs the workshop upload after fixing the credentials.

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

With one exception, do not submit fully AI-written pull requests/bug reports. If I wanted a chatbot's input, I'd prompt it myself. Please don't act as a middleman dumping output that I have to sort through and fix.

