# Installing OS packages


```
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
sudo dnf upgrade
# sudo dnf install open-vm-tools open-vm-tools-desktop   # to as a Test VM
sudo dnf install java-21-openjdk java-21-openjdk-devel # for Jenkins support
sudo dnf install vim
sudo dnf install git
sudo dnf-install net-tools
sudo dnf install python3
sudo dnf install python3-pip
sudo dnf install python3-tkinter
sudo dnf install python3-pytest
sudo dnf install pyside6*
sudo dnf install pytest
sudo dnf install python3-astroid
sudo dnf install python3-pylint
```

On Rocky 8/9, install the following:

```
sudo dnf install qt6-qtbase qt6-qtbase-gui
sudo dnf install python3-pyside6 pyside6-tools   # optional, for PySide6 itself
```

for the QT_QPA_PLATFORM='offscreen' environment variable to work.

For Rocky 10 to work:

```
sudo dnf install qt6-qtbase qt6-qtbase-gui
```


# Installing useful apps with dnf

```
sudo dnf install epel-release
sudo dnf install meld
```
---

# Installing

```
```

# Installing manually from vendor



# Installing python modules

```
```

---

# Setting up ssh server

```
sudo apt update
sudo apt upgrade
sudo apt install openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh
sudo vim /etc/ssh/sshd_config
```
