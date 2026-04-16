# ssh with ssh key

## on source machine:

```
ssh-keygen -t ed25519 -C "your_email@example.com" -f <key-name>
ssh-copy-id -i <key-name>.pub user@remote_host
eval $(ssh-agent)
ssh-add <key-name>
```

## on destination machine

Check the /etc/ssh/sshd_config for the following directives before taking the above steps:

```
Port 22                  # Default SSH port
PermitRootLogin no       # Disable root login for security
PasswordAuthentication yes  # Allow password login (or set to 'no' if using keys only)
PubkeyAuthentication yes # Enable public key authentication
```

Then run:

```
sudo systemctl enable ssh
sudo systemctl restart ssh
```

## Across Reboots

Yes ✅ — you can make sure your SSH keys are automatically added to the `ssh-agent` across reboots, so you don’t have to run `ssh-add` manually every time. The exact method depends on your operating system and environment:

---

### 🐧 Linux (most distros)

#### 1. **Use `ssh-agent` with your desktop environment**

- **GNOME / KDE**: These environments usually start `ssh-agent` automatically when you log in.
- To ensure your key is added:
    
    ```bash
    ssh-add ~/.ssh/id_ed25519
    ```
    
    Then add that command to your **login scripts**:
    - `~/.bash_profile` or `~/.bashrc`
    - Or use your desktop’s “Startup Applications” settings.

---

#### 2. **Systemd integration (modern distros)**

You can configure `ssh-agent` as a systemd user service:

```bash
systemctl --user enable ssh-agent
systemctl --user start ssh-agent
```

Then add your key permanently:

```bash
ssh-add ~/.ssh/id_ed25519
```

To avoid retyping the passphrase, you can use **keychain** (see below).

---

### 🍎 macOS

- macOS has built-in support for storing SSH keys in the **Keychain**.
- Add your key with:
    
    ```bash
    ssh-add --apple-use-keychain ~/.ssh/id_ed25519
    ```
    
- Then edit `~/.ssh/config` to include:
    
    ```text
    Host *
      UseKeychain yes
      AddKeysToAgent yes
      IdentityFile ~/.ssh/id_ed25519
    ```
    

This ensures your key is automatically loaded after reboot.

---

### 🪟 Windows (with OpenSSH)

- If you’re using Windows 10/11 with OpenSSH:
    
    ```powershell
    ssh-add ~\.ssh\id_ed25519
    ```
    
- To persist across reboots, you can add the command to your **PowerShell profile** or use the **Windows Credential Manager** to store the passphrase.

---

### 🔑 Extra Tool: `keychain`

On Linux, a popular helper is [`keychain`](https://www.funtoo.org/Keychain):

- It wraps `ssh-agent` and remembers your keys across logins.
- Install:
    
    ```bash
    sudo apt install keychain   # Debian/Ubuntu
    ```
    
- Add to `~/.bashrc`:
    
    ```bash
    eval $(keychain --eval id_ed25519)
    ```
    

This way, you only enter your passphrase once per boot, and all shells reuse the agent.

---

### ⚡ Summary

- **Linux**: Use systemd user service or `keychain`.
- **macOS**: Use `UseKeychain` in `~/.ssh/config`.
- **Windows**: Use Credential Manager or PowerShell profile.

---

Would you like me to show you the **systemd user service setup** in detail (with the unit file example), since that’s the most robust way on modern Linux systems?


## Can one install on RHEL or Rocky Linux?

**Yes — you can install `keychain` on both Red Hat Enterprise Linux (RHEL) and Rocky Linux.** It’s available through standard package managers (`yum` or `dnf`) and works as a front‑end to `ssh-agent`, making SSH key management persistent across logins and reboots [Installati.one](https://installati.one/install-keychain-rockylinux-8/).

---

### 🔧 How to Install `keychain` on RHEL/Rocky Linux

#### 1. **Check Availability**

On Rocky Linux 8 (and similar RHEL versions), `keychain` is in the repositories:

```bash
sudo dnf install keychain -y
```

or, if using older RHEL:

```bash
sudo yum install keychain -y
```

#### 2. **Verify Installation**

```bash
keychain --version
```

---

### ⚙️ Configure `keychain`

After installation, you need to integrate it with your shell so it runs automatically at login:

1. Edit your shell startup file (`~/.bashrc`, `~/.bash_profile`, or `~/.zshrc`):
    
    ```bash
    eval $(keychain --eval id_ed25519)
    ```
    
    Replace `id_ed25519` with the name of your SSH key (e.g., `id_rsa`).
    
2. Log out and back in, or reload your shell:
    
    ```bash
    source ~/.bashrc
    ```
    
3. On first login after reboot, you’ll be prompted for your key’s passphrase. After that, `keychain` keeps the agent alive, so subsequent logins won’t require re‑entering it.
    

---

### 📌 Why Use `keychain` on RHEL/Rocky

- **Convenience**: Enter your passphrase only once per reboot.
- **Security**: Encourages strong passphrases without sacrificing usability.
- **Multi‑session support**: Works across multiple terminals and remote logins.
- **Compatibility**: Supports OpenSSH, ssh.com, Sun SSH, and GnuPG agents [Installati.one](https://installati.one/install-keychain-rockylinux-8/).

---

### ⚠️ Considerations

- On hardened RHEL systems, you may need to enable **EPEL (Extra Packages for Enterprise Linux)** if `keychain` isn’t in the base repo.
- Always ensure your SSH keys are stored securely (`~/.ssh` with proper permissions).
- If you use multiple keys, you can list them all:
    
    ```bash
    eval $(keychain --eval id_ed25519 id_rsa)
    ```
    

---

✅ In short: **Yes, `keychain` is installable on RHEL and Rocky Linux via `dnf`/`yum`, and it’s a great way to persist SSH keys across sessions.**

Would you like me to show you the **exact steps for enabling EPEL on RHEL/Rocky** in case `keychain` isn’t found in your default repos?


