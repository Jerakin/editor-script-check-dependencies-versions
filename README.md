# Check Dependencies

> [!NOTE]
> If you can not get this editor script to work you can always run the python script from your command line.
> Download the python file, within your CMD/Terminal navigate to your project then run the script.

## Install
You can use the these editor scripts in your own project by adding this project as a [Defold library dependency](https://www.defold.com/manuals/libraries/). Open your game.project file and in the dependencies field under project add:  
https://github.com/Jerakin/editor-script-check-dependencies-versions/archive/master.zip

### Dependencies
You also need to make sure you have python 2.7 or newer.

## Editor Script
This script adds a item under `view`. Running the command will print out the states of your dependencies to the console.

```
Project 'defold-clipboard' is up to date.

Project 'defold-lfs' is outdated, latest version is
  https://github.com/britzl/defold-lfs/archive/1.0.1.zip
  
Project 'extension-gps' is up to date.

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
