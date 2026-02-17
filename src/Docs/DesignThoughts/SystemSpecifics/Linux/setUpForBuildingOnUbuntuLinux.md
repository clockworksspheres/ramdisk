# Install on Ubuntu Server

Once the server is installed:

```
sudo apt upgrade
sudo apt install kde-standard
sudo apt install net-tools
sudo apt install open-vm-tools open-vm-tools-desktop
sudo apt install openjdk-21-jdk
```

Installing "kde-standard" will take some time.

# Installing and Setting Up OS packages

```
sudo ln -s /usr/bin/python3 /usr/local/bin/python
sudo apt install python3-tk
sudo apt install python3-pip
sudo apt install python3-pytest
sudo apt install python3-venv
sudo apt install vim
sudo apt install git
sudo apt install dia dia-common dia-shapes dia2code
sudo apt install slack
sudo apt install vym
sudo apt install umbrello
sudo ln -s /usr/bin/umbrello5 /usr/local/bin/umbrello
sudo apt install meld
sudo apt install qtcreator
```

# Installing via snap

```
sudo apt install snapd
sudo snap install core
sudo snap refresh core
sudo snap install brave
sudo snap install obsidian --classic # does not work on arm platforms
sudo snap install drawio # does not work on arm platforms
sudo snap install zotero-snap # does not work on arm platforms, must be executed as zotero-snap
```
# Installing

```
```

# Installing manually from vendor

Download positron from: https:/github.com/posit-dev/positron/releases

```
sudo dpkg -i Positron-25.11.0-234-arm64.deb # (on arm64 - macos VM)
```

# Cannot install on arm64

* obsidian
* drawio (install dia and friends instead)
* zotero

# Setting up ssh server with git

```
sudo apt update
sudo apt upgrade
sudo apt install openssh-server
sudo ufw allow ssh
sudo systemctl enable --now ssh
sudo systemctl status ssh
sudo vim /etc/ssh/sshd_config
```

make sure the line  ``` PermitRootLogin no ``` is in the file.  if not, put it in near the *PermitRootLogin* line is in.

put the next to lines in there as well:

```
PermitRootLogin no
PasswordAuthentication yes
PermitEmptyPasswords no
PubkeyAuthentication yes
MaxAuthTries 6
MaxSessions 10
```

comment out:

```
#KbdInteractiveAuthentication no
```

run:

```
sudo systemctl restart ssh
ip addr show
```

reboot

scp the appropriate keys from a current machine that works with git to the new VM.

https://docs.github.com/en/authentication/connecting-to-github-with-ssh

check out that site if you don't already have keys to use, or want to create new keys.

```
vim ~/.ssh/config
```

add the following:

```
HOST github.com
     IdentityFile <privatekey>
```

run:

```
ssh-add ~/.ssh/<githubprivatekey>
cd <clockworksspheres-dir-root>
```

Now you should be able to download via ssh your github project, that you have rights to.

```
git clone git@github.com:clockworksspheres/ramdisk
```

# Jenkins setup

On the Jenkins server, copy the public jenkins user key to the jenkins user on the VM/Machine:

```
ssh-copy-id -i <key-name>.pub user@remote_host
```

On the Ubuntu machine, create an /etc/sudoers.d/<jenkins-user> file with the following content:

```
<jenkins-user> ALL=(ALL) NOPASSWD:/usr/bin/py.test
```

You should now be able to add this machine as a node to the Jenkins server.