# Mod file locations on disk

## Where are the files for a workshop mod?
The easiest way is to use the Paradox Launcher or something like [Irony Mod Manager](https://bcssov.github.io/IronyModManager/) and their "open mod folder" feature.

![image](https://github.com/Aerolfos/stellaris_mod_deploy_action/assets/8443014/ef6cdcee-e33c-4980-9ba8-7978151cc075)

With for example the [Gigastructures mod](https://steamcommunity.com/sharedfiles/filedetails/?id=1121692237), you would find it at `Steam/steamapps/workshop/content/281990/1121692237`. Read on for why it's there specifically.

The Steam folder is wherever you installed Steam or, by using the Steam storage feature, wherever you installed Stellaris. Right click on Stellaris, properties, Installed Files, and Browse to find it easily. Go up two folders to find the `workshop` folder.

![image](https://github.com/Aerolfos/stellaris_mod_deploy_action/assets/8443014/1dea76cb-075e-48c2-b45c-0c39aa4b7fdc)


### How can you find out what the numbers are/should be?
Stellaris' ID is `281990` in the Steam store - it's simply the numbers on the link: https://store.steampowered.com/app/281990/Stellaris/

And a mod's ID is the same, `1121692237` for this mod from: https://steamcommunity.com/sharedfiles/filedetails/?id=1121692237

Workshop mods are simply stored in the `workshop/content/` folder grouped in a folder for the game, and then a folder for each mod - `workshop/content/stellaris_id/mod_id`. You can grab the numbers and put them into a link and find out which game/mod you're looking at that way.

## Where are local files for mods/where do you go for manual installation?
Mods managed by the [stellaris_mod_deploy_action](https://github.com/Aerolfos/stellaris_mod_deploy_action) these pages belong to have [dedicated installation instructions](https://github.com/Aerolfos/stellaris_mod_deploy_action/wiki/Mod-installation).

On Windows, to: `%USERPROFILE%/Documents/Paradox Interactive/Stellaris/mod`

You can copy and paste that address directly into explorer:
![image](https://github.com/Aerolfos/stellaris_mod_deploy_action/assets/8443014/8d488633-355f-47a7-8f15-5b7415cbaefb)

Alternatively,
- GNU/Linux: `~/.local/share/Paradox Interactive/Stellaris/mod/`
- Mac: `~/Documents/Paradox Interactive/Stellaris/mod/`

Mods should come as a folder `mod_folder_name` and a `.mod` file with the same name as the folder. The file is a simple text type, the extension is just an identifier for the paradox launcher.

## See also: [https://stellaris.paradoxwikis.com/Mods](https://stellaris.paradoxwikis.com/Mods)
