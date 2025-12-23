# Set Up For Building on Windows

Installing tools to set up for building the project.  Some help gained from AI, either grok.com or copilot.com.

## Install Chocolatey

Chocolatey is a package manager for Windows, similar to homebrew for macos, apt for debian linux based systems and yum/dnf for redhat based systems.

To install chocolatey, open an admin powershell, and run the following:

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

To use chocolatey, close the powershell window, and open a new admin powershell window.

## Set up Chocolatey to run as a User

 **NOTE** you need Chocolatey for Business to install chocolatey in a user context work.

## Install software required for the project

* python (not the latest version as pyside6 doesn't work with it)
* git
* obsidian
* less
* favorite editor (project prefers positron)

### With Chocolaty

```
choco install python312
choco install git
choco install less
choco install obsidian
```

Download and install positron from:  https://positron.posit.co/download.html

To be able to use the command line tools above, you will need to close the powershell window, then open a new powershell window.

Git, less and python should now be in the administrative shell path and work fine now.

Run:

```
git config --global core.autocrlf false
```

or git will change all the \*nix lf's to crlf's making all files have an extra line between everything on linux and macos.  Windows does not need crlf's, git just likes to be helpful and re-arrange everything for you on Windows.

## Useful software to consider installing

* brave browser (or other favorite browser)
* drawio
* geany
* meld
* pytest
* qtcreator
* rsync
* slack or other 'community software' like pidgin or discord (for OS specific communities)
* tree
* umbrello
* vscode
* vym (if available)
* webex
* zoom
* zotero

### With Chocolatey 

```
choco install drawio
choco install brave
choco install meld
choco install qtcreator
choco install qt6-base-dev
choco install rsync
choco install slack
choco install tree
choco install vscode
choco install umbrello
choco install webex
choco install zoom
choco install zotero
```

to see if a piece of software is available via chocolatey, you can do:

```
choco search softwareName
```

like searching for the brave browser:

```
choco search brave
```

To make sure the software you are searching for is the right software, run:

``` 
choco info brave
```

to find out a variety of information on the brave chocolatey package.

### Without Chocolatey

Vym - Download and install the vym exe installer from: https://sourceforge.net/projects/vym/files/ - if the latest .exe is very far out of date, you can go into the Development directory and install the exe in there - but be aware that is an EXPERIMENTAL version.

Download and install CMake from: https://cmake.org/download/ (restart any powershell windows that are open, to be able to use cmake)

Download and install Qt6 - open source - https://www.qt.io/download-qt-installer-oss (one has to make an account and agree to the terms of service)

### From the Microsoft Store

A few other possible editors from the Microsoft Store:

* Code::Blocks
* Visual Studio Code
* Visual Studio Community

## Set up git to connect to github with ssh



## Setting up the terminal and powershell to start and your user home



```
$USERNAME = <your username here>
icacls $PROFILE /grant "$env:USERNAME":RX
icacls $PROFILE /grant "$env:USERNAME":RX
icacls $PROFILE /remove:g Guests
notepad $PROFILE
```

and put the following into that file:

```
Set-Location $HOME
```

and that should fix your command shells.

