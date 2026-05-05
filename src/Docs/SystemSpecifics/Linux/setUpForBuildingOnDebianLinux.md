# setUpForBuildingOnDebianLinux

# Installing OS packages

Put user in group file, under "sudo".  Then reboot.

```
sudo apt install net-tools
sudo apt install vim
sudo apt install git
sudo apt install python3-pip
sudo apt install python3-venv
sudo apt install python-is-python3
sudo apt install junit
sudo apt install python3-pyside6
sudo apt install python3-pytest
sudo apt install python3-pylint-common
sudo apt install python3-astroid
```

# Installing useful apps with apt

```
sudo apt install dia dia-common dia-shapes dia2code
sudo apt install slack
sudo apt install vym
sudo apt install umbrello5
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

# Setting up ssh

This is the preferred method for this project for jenkins pipeline setup, the other is undocumented.

### ssh server side, ie VM guest

```
sudo apt update
sudo apt upgrade
sudo apt install openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh
sudo vim /etc/ssh/sshd_config
```

Ensure the following lines are in and uncommented the /etc/ssh/sshd_config file:

```
PasswordAuthentication no
PubkeyAuthentication yes
```

After changing those lines, restart sshd:

```
sudo systemctl restart sshd
```


### on the client side - machine you are ssh'ing from, like the jenkins server:

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Copy the public key from the host that created the ssh keys to the ssh server:

```
ssh-copy-id -i ~/.ssh/<custom_key_name>.pub username@remote_ip_or_hostname
```

Make sure the authorized keys file on ```username@remote_ip_or_hostname``` has the following permissions:

```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/<custom_key_name>*
```

Make sure that the same are correct on the server side

```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

 **Common pitfalls (where most people get stuck)**

- Wrong permissions on `~/.ssh` or `authorized_keys`
- Key not added to agent
- Connecting as wrong user
- Server still forcing password auth
- Using the wrong key (multiple keys on system)
- Check the ~/.ssh/known_hosts file for multiple of the same key, or clashes of the same hostname/IP address with different hashes.

# Setting up ssh with git

Follow this document for connecting to github with ssh - using the keys made above:

https://docs.github.com/en/authentication/connecting-to-github-with-ssh

check out that site if you don't already have keys to use, or want to create new keys.  The site also has validation and testing steps to make sure the ssh method of connecting with github is working .

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

# Chat Prompt: how do I set up NOPASSWD for a binary that might be at different locations?

 - Setting up sudo on guest vm's to allow for pipleline testing 

You’re running into a real limitation of `sudo`: it matches **exact command paths**, not “any binary with this name anywhere.” There’s no native wildcard like “any path ending in `/mytool`”.

So if you need `NOPASSWD` for something that can live in different locations, you’ve got a few solid patterns—some safe, some… less so.

---

## ✅ Best Practice: Use a Stable Wrapper (recommended)

Create a fixed path that `sudo` can trust, and let that call your “moving target.”

### 1. Create a wrapper script

```bash
sudo install -m 0755 /dev/stdin /usr/local/bin/mytool-wrapper <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Resolve actual binary dynamically
if command -v mytool >/dev/null 2>&1; then
    exec "$(command -v mytool)" "$@"
else
    echo "mytool not found in PATH" >&2
    exit 1
fi
EOF
```

---

### 2. Add sudoers entry

Edit safely:

```bash
sudo visudo
```

Add:

```
youruser ALL=(ALL) NOPASSWD: /usr/local/bin/mytool-wrapper
```

---

### 3. Use it

```bash
sudo mytool-wrapper arg1 arg2
```

---

## ⚠️ Why this is the right approach

- `sudo` only trusts **explicit paths**
    
- You avoid:
    
    - PATH injection attacks
        
    - Users swapping binaries
        
    - Privilege escalation via writable directories
        

---

## 🚫 Things you _should not_ do (unless you fully accept the risk)

### 1. Wildcards in sudoers

You _can_ do:

```
youruser ALL=(ALL) NOPASSWD: /usr/bin/*mytool*
```

But:

- This matches filenames, not arbitrary directories
    
- It’s dangerous if users can write to those locations
    

---

### 2. Allowing a directory

```
youruser ALL=(ALL) NOPASSWD: /opt/tools/*
```

Risk:

- If the user can write to `/opt/tools`, they can drop a malicious binary and run it as root
    

---

## 🔒 More Secure Variant (strict path control)

If you know possible locations:

```
Cmnd_Alias MYTOOLS = /usr/bin/mytool, /usr/local/bin/mytool, /opt/mytool/bin/mytool

youruser ALL=(ALL) NOPASSWD: MYTOOLS
```

---

## 🔥 Advanced Option: Lock down environment

In sudoers:

```
Defaults!MYTOOLS secure_path="/usr/sbin:/usr/bin:/usr/local/bin"
```

Prevents PATH tricks.

---

## 🧠 Subtle gotcha

Even this is unsafe:

```
NOPASSWD: mytool
```

Because:

- `sudo` does NOT resolve via your shell’s PATH the way you expect
    
- It can behave inconsistently and insecurely
    

Always use **absolute paths or a wrapper**.

---

## 🧩 If this ties into your CLI tooling (like your `vmm` project)

The wrapper approach is ideal because you can:

- Normalize behavior across hypervisors
    
- Control execution logic
    
- Add logging / auditing
    
- Enforce argument validation before root execution
    

---

## If you want next-level setup

I can help you:

- Build a **secure command dispatcher** (like a mini sudo gateway)
    
- Generate sudoers rules automatically from your CLI
    
- Add **argument whitelisting** (very useful for VM control)
    
- Integrate with **polkit** instead of sudo for finer control
    

Just tell me your use case.