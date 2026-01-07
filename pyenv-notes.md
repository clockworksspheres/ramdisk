# Pyenv notes


# Setting up venv for this project

On macOS and Linux

``` bash
cd src
directory="./packenv"
actfile="./packenv/bin/activate"

if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then

   python3 -m venv packenv

   source packenv/bin/activate

   pip3 install PySide6 PyInstaller
   pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
   pip3 install packaging

else
   source packenv/bin/activate
fi
export PATH=".":$PATH

```

It's easiest if you cd into the src directory first.

Each time you go to run files in this directory tree, it's easiest if you go to the "src" directory and run:

``` bash
source packenv/bin/activate
```

This will set up the same setup across operating systems.

There will be a build file for each OS creating an app or app bundle for the GUI version of the program.  The gui portion of the program is written in Pyside6.  The way to bypass the GUI and run at the command line is to give specific parameters for -s and -m.  If one wants to just hook into the ramdisk code where it will spawn a ramdisk, the same way on each of the operating systems, take a look at the src/ramdisk-setup.py and src/examples/setup_ramdisk_example.py. 

# About pyenv

Pyenv provides a framework for managing different versions of python, so one can manage the version of python one uses for different classes, courses, projects, etc.

Please note: some videos install tools straight from github - some can be installed using the 'pip' method, or downloading directly from pypi.org

The [pyenv project on github](https://github.com/pyenv/pyenv)

Decent instructions there - 

## Some youtube videos

Linux
* https://www.youtube.com/watch?v=JyimhcbZ-8w
* https://www.youtube.com/watch?v=KL7HRhE9g7A
* https://www.youtube.com/watch?v=fv8YxO3AJqg


### macOS
* https://www.youtube.com/watch?v=9UxSStjelNg
* https://www.youtube.com/watch?v=cY2NXB_Tqq0


### Windows
* https://www.youtube.com/watch?v=vG2yWK87TCY


### Cross platform
* https://read.acloud.guru/my-python-setup-77c57a2fc4b6


### Additional, some what related tools
* venv, pyenv, pypi, pip, pipenv, py
* WTF? https://www.youtube.com/watch?v=-C8uVImkTQg




 

