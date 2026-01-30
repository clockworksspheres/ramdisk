# Installing OS packages

Setup *DOES NOT WORK* on aarch64 Rocky 10.

```
sudo dnf upgrade
sudo dnf install -y epel-release
sudo dnf install vim
sudo dnf install git
sudo dnf-install net-tools
sudo dnf install python3
sudo dnf install python3-pip
sudo dnf install python3-tkinter
sudo dnf install junit.noarch
sudo dnf install minizip-ng-compat
sudo dnf install xcb-util-wm
sudo dnf install libxcb-cursor.aarch64
sudo dnf install xcb-util-cursor.aarch64
sudo dnf install xcb-util-keysyms.aarch64
sudo dnf install open-vm-tools
sudo dnf install open-vm-tools-desktop
pip install pytest
```

# Installing useful apps with dnf

```
dnf install meld
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

# Installing Rocky in WSL

``` powershell
# -----------------------------  
# Rocky Linux WSL Install Script  
# Downloads Rocky 8 & 9 WSL images and installs them into WSL2  
# -----------------------------  
  
# Create a working directory  
mkdir C:\WSL\Rocky -Force  
cd C:\WSL\Rocky  
  
# -----------------------------  
# Download Rocky Linux 8 WSL image  
# -----------------------------  
Invoke-WebRequest `  
-Uri "[https://dl.rockylinux.org/pub/rocky/8/images/Rocky-8-WSL-Base.latest.x86_64.wsl](https://dl.rockylinux.org/pub/rocky/8/images/Rocky-8-WSL-Base.latest.x86_64.wsl)" `  
-OutFile "Rocky-8.wsl"  
  
# Create install directory for Rocky 8  
mkdir C:\WSL\Rocky8 -Force  
  
# Install Rocky Linux 8 into WSL2  
wsl --install --from-file .\Rocky-8.wsl --name Rocky8  
  
# -----------------------------  
# Download Rocky Linux 9 WSL image  
# -----------------------------  
Invoke-WebRequest `  
-Uri "[https://dl.rockylinux.org/pub/rocky/9/images/Rocky-9-WSL-Base.latest.x86_64.wsl](https://dl.rockylinux.org/pub/rocky/9/images/Rocky-9-WSL-Base.latest.x86_64.wsl)" `  
-OutFile "Rocky-9.wsl"  
  
# Create install directory for Rocky 9  
mkdir C:\WSL\Rocky9 -Force  
  
# Install Rocky Linux 9 into WSL2  
wsl --install --from-file .\Rocky-9.wsl --name Rocky9  
  
# -----------------------------  
# Optional: Set Rocky 9 as default  
# -----------------------------  
wsl --set-default Rocky9  
  
# -----------------------------  
# Launch both distros once to initialize  
# -----------------------------  
wsl -d Rocky8  
wsl -d Rocky9
```