# Potential features

A list of potential features I thought of but didn't get around to actually implementing, or which are not possible for some reason. This is a list of ideas and not a TODO-list or similar, most of these are scope creep not worth working on.

## Paradox mods auto uploading

Paradox doesn't supply a user-facing API so this simply can't be done. If we get one, that could change.

## Extra overrides

- Override changelog format to use - probably in file in target mod repo

- Override for both template file and search string to pair with it

- Mod folder name

- Ability to override repo name being the same as mod folder name

## Different supported mod structures

Currently, mods must be nested in a particular format. Changing this would require a way of specifying what files to include as actual mod files to be uploaded/zipped, so a blacklist/whitelist system. The whitelist must be maintained by the user, and could be a source of issues if for example new folders are added to the base game. If a user forgets to update their whitelist, new folders would not be included and the mod breaks.

The [`mod/mod_name/mod_name/common/` structure](../Tool%20support/expected_mod_structure.md) would probably still be recommended.

## Other Paradox games

The Grand Strategy titles that use the launcher and `.mod` file system should already be supported. This is only here because I haven't actually tested compatibility.

## Starter workflow/workflow template

See: https://docs.github.com/en/actions/using-workflows/creating-starter-workflows-for-your-organization

Might be helpful as one way to improve setup/onboarding?

## Repository template

In a similar vein, provide a clean repository that one can fork/clone and then either start a new mod or copy an existing one's file and information into the repository. The necessary hookups for the deployment tool would already be provided.

## Webhook compat

Set up workflow to be triggerable from a webhook, rather than from inside GitHub actions panel. In theory, it should be possible to trigger an update from say a discord channel command. Scope creep, really.

## Webhook output

You can get action runs as is via webhook, but it might be valuable to have a custom message that outputs a release link and/or posts the changelog somewhere, automatically. Requires a disproportionate amount of setup to make happen.

## Steam workshop auto uploading

(Yeah this worked it's implemented now)

TODO clean up here

So *in theory* this is possible by using and setting up [SteamCMD](https://developer.valvesoftware.com/wiki/SteamCMD) somehow. However, having SteamCMD running conflicts with the normal steam app and there's no way you should be handing your main account over to the cloud for use like this.

But, since it's now actually possible to update mod files as a contributor, it's in theory possible to make a development account, add it as contributor, save the credentials via the GitHub secret system (which should properly encrypt them) and then it might work out to have that account get logged in to upload files from one of GitHub's runners. Problem is you must own the game to use the workshop for it, so you'd have to buy Stellaris for a test account, just to see if it will even work after all the work of implementing the upload system.

## Mirroring workshop description and GitHub README

Changing over Markdown formatting to the closest equivalent Steam BBCode. Wouldn't be perfect and copying formatting and description exactly may be undesirable. 

