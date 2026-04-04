# Installing from GitHub
See also [the Stellaris Wiki page on installation for local mods](https://stellaris.paradoxwikis.com/Mods#Installation).

This guide is for installing mods with a [GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases), preferentially ones managed by the [stellaris_mod_deploy_action](https://github.com/Aerolfos/stellaris_mod_deploy_action). If the release had a link here it is probably using this tool. A mod release should have the following files attached:

![release_attached_files](https://github.com/user-attachments/assets/505f0023-02e6-4400-ad4e-44eb74d16997)

Download the `ModName_version.zip` by clicking on it, and unzip the downloaded archive. Depending on your OS and settings, it will either make a folder with the same name as the zip, which contains a `ModName` folder and `ModName.mod` file, or yield these two objects directly (into your downloads folder). You want the folder and `.mod` file.

A `.mod` file is a plain text file with a custom extension, make sure ["show file extensions" is enabled in Windows](https://support.microsoft.com/en-us/windows/common-file-name-extensions-in-windows-da4a4430-8e76-89c5-59f7-1cdbbc75cb01).

![files_you_want_illustration](https://github.com/user-attachments/assets/57a0a282-6ae7-4af1-9cb6-74c5b15519e6)

Now navigate to the Stellaris local mods folder - for convenience use a new tab or new window in your file explorer. You find this at:

- Windows: `%USERPROFILE%\Documents\Paradox Interactive\Stellaris\mod\`
- GNU/Linux: `~/.local/share/Paradox Interactive/Stellaris/mod/`
- Mac: `~/Documents/Paradox Interactive/Stellaris/mod/`

You can paste the path into your explorer navigation bar directly:

![pasting_into_explorer_navigation](https://github.com/user-attachments/assets/d8a34078-f75a-4fe3-939e-8be2a55be1bc)

If applicable, remove any previous installation of the mod (mod folder and .mod file). This is very important, as the game loads all files present in mod folder, which may result in conflicts and things not working properly.

Now drag and drop the folder and `.mod` file into the Stellaris mod folder.

![drag_and_drop_illustration](https://github.com/user-attachments/assets/be7a48ef-bfbc-4783-a660-df04835e2105)

The mod should now show up in the Paradox Launcher or alternative mod managers and works the same as a workshop subscribed mod from this point on.

Your `[...]/Paradox Interactive/Stellaris/mod` folder should contain the `ModName` folder and `ModName.mod` file, if the folders are arranged differently things won't work.

Mods that use the [stellaris_mod_deploy_action](https://github.com/Aerolfos/stellaris_mod_deploy_action) should have correct paths when downloaded directly and need no modification, but this may not be the case for other mods. It will guaranteed *not* be the case for mods from the workshop. [See the Paradox Wiki](https://stellaris.paradoxwikis.com/Modding#Mod_management) on how mods and in particular the `.mod` file work in the general case. See also [this page for where workshop mods end up](https://github.com/Aerolfos/stellaris_mod_deploy_action/wiki/Mod-file-locations).

### For developers

Note, for a mod with a Github version it is possible to clone the repository through usual Github methods into the `[...]/Paradox Interactive/Stellaris/mod/` folder, create the necessary .mod file or generate it, and keep the mod up to date with Github tools. See [for example this page](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-a-repository-from-github-to-github-desktop). Getting updates for a local copy is much easier this way, if you want the absolute latest in dev changes as they happen. These are probably not entirely stable and bugs can be expected.

[Irony Mod Manager](https://bcssov.github.io/IronyModManager/) will autogenerate the necessary `.mod` file based on the mods internal `descriptor` file. Cloning a repo and using Irony Mod Manager is the better way to handle mod development/forking. For playing, just use the stable releases.
