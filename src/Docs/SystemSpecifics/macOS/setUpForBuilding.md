# Set Up For Building on macOS

## Install the macos Command Line Tools

Run the following command at the command line:

``` sh
xcode-select --install   
```

## Install the Homebrew package manager

Run the following at the command line:

``` sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Install software required for the project

* pyenv
* python (not the latest version as pyside6 doesn't work with it)
* git
* obsidian
* favorite editor (project prefers positron)


### With homebrew

``` sh
brew install pyenv
brew install git
brew install obsidian # to maintain .md files in the repo
brew install positron
```

### Install python that's not the latest version

Pyside6 doesn't support the latest version of python.

``` sh
pyenv install 3.12.12 # or other/similar specific older version
pyenv global 3.12.12. # to set that version as the user system specific version of python
```

you may need to restart your shell for this version of python to be recognized.  

## Useful software to consider installing

* drawio
* brave browser (or other favorite browser)
* slack or other 'community software' like pidgin or discord (for OS specific communities)
* vym
* pytest
* meld
* qtcreator
* zotero

### With homebrew:

``` sh
brew install drawio
brew install brave-browser
brew install slack
brew install vym
brew install pytest
brew install meld
brew install qtcreator
brew install zotero
```

## Set up git to connect to github with ssh

