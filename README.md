# Check Dependencies

## Install
You can use the these editor scripts in your own project by adding this project as a [Defold library dependency](https://www.defold.com/manuals/libraries/). Open your game.project file and in the dependencies field under project add:  
https://github.com/Jerakin/editor-script-check-dependencies-versions/archive/master.zip

### macOS
You need to make your python installation visible to Defolds Java VM, you need to put your path modifications in
`$HOME/.bash_profile`. This is because I `source $HOME/.bash_profile` and I opted do it this way instead of
`export PATH="$PATH:/usr/local/bin"` because if you are using `pyenv` and `pyenv-virtualenv` it would not pick up on that.

### Dependencies
You also need to make sure you have python 2.7 or newer.

## Editor Script
This script adds a item under `view`. Running the command will print out the states of your dependencies to the console.

```
Project 'defold-clipboard' is up to date.

Project 'defold-lfs' is out dated, latest version is
  https://github.com/britzl/defold-lfs/archive/1.0.1.zip
  
Project 'extension-gps' is up to date.

```

## Rate limited
This script is working against the github api v3 which rate limits calls, I think that for normal use the rate limit
should be enough. But if the script ever mentions that you are rate limited then I recommend that you set up a token.

In your root create a file named `editor-script-check-dependencies` (no extension) inside a folder `.editor-script-settings/` (notice the prefix `.`)

Add this in the file where TOKEN is a personal token [GUIDE: Personal Token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)
```
[Authenticate]
token = TOKEN
```

DO NOT COMMIT THIS FILE TO YOUR REPOSITORY!