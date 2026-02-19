# Installing OS packages

Setup *DOES NOT WORK* on aarch64 Rocky 10.

```
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
sudo dnf upgrade
sudo dnf install open-vm-tools open-vm-tools-desktop   # to as a Test VM
sudo dnf install java-21-openjdk java-21-openjdk-devel # for Jenkins support
sudo dnf install vim
sudo dnf install git
sudo dnf-install net-tools
sudo dnf install python3
sudo dnf install python3-pip
sudo dnf install python3-tkinter
sudo dnf install python3-pytest
```

# Installing useful apps with dnf

```
sudo dnf install epel-release
sudo dnf install meld
```
---

# This is as far as I could get with the Rocky 10 install

My python apps still work with the above packages installed.

Some SELINUX errors of needing a newer version than the mirror provides for installing snapd

---

# Installing

```
```

# Installing manually from vendor



# Installing python modules

```
```

