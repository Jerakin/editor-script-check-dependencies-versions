# Check Dependencies

## Install
You can use the these editor scripts in your own project by adding this project as a [Defold library dependency](https://www.defold.com/manuals/libraries/). Open your game.project file and in the dependencies field under project add:  
https://github.com/Jerakin/editor-script-check-dependencies-versions/archive/master.zip

## Editor Script
This script adds a item under `view`. Running the command will print out the states of your dependencies to the console.

```
editor-script-check-depedendencies
 ✔  The dependency is up to date.
 ✖  The dependency is outdated.
 !  The dependency is not using a semver supported release.


✔ defold/extension-safearea (1.5.1)
    https://github.com/defold/extension-safearea/archive/1.5.1.zip

✖ defold/extension-safearea (1.0.0)
    https://github.com/defold/extension-safearea/archive/1.5.1.zip

! britzl/monarch (master)
    https://github.com/britzl/monarch/archive/5.1.1.zip

```

## Rate limited
This script is working against the github api v3 which rate limits calls, I think that for normal use the rate limit
should be enough. But if the script ever mentions that you are rate limited then I recommend that you set up a token.

In your root create a file at `./.editor-script-settings/editor-script-check-dependencies` (no extension and . infront of editor-script-setting).

Add this to the file where TOKEN is a personal token [GUIDE: Personal Token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
```
[Authenticate]
token = TOKEN
```

THE TOKEN IS A SECRET SO DO NOT COMMIT THIS FILE TO YOUR REPOSITORY!
