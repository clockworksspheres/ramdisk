# setUpForBuildingOnDebianLinux

# Installing OS packages

Put user in sudoers file

```
sudo dnf makecache
sudo apt install net-tools
sudo apt install vim
sudo apt install git
sudo apt install python3-tk
sudo apt install python3-pip
sudo apt install python3-pytest
sudo apt install python3-venv
sudo ln -s /usr/bin/python3 /usr/local/bin/python
sudo apt install junit
```

# Installing useful apps with apt

```
sudo apt install dia dia-common dia-shapes dia2code
sudo apt install slack
sudo apt install vym
sudo apt install umbrello
ln -s /usr/bin/umbrello5 /usr/local/bin/umbrello
sudo apt install meld
sudo apt install qtcreator

```

# Installing useful apps with snap

```

```

# Installing

```
```

# Installing manually from vendor

Download positron from: https:/github.com/posit-dev/positron/releases

```
sudo dpkg -i Positron-25.11.0-234-arm64.deb # (on arm64 - macos VM)
```


# Setting up ssh server with git

```
sudo apt update
sudo apt upgrade
sudo apt install openssh-server
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
ssh-add ~/.ssh/<privatekey>
cd <clockworksspheres-dir-root>
```

Now you should be able to download via ssh your github project, that you have rights to.

```
git clone git@github.com:clockworksspheres/ramdisk
```

