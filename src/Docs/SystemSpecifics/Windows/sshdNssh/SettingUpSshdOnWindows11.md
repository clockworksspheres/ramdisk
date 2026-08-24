# Setting up sshd on Windows 11

First, remove the old bult in OpenSSH

```
Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Remove-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

# Grok conversation

## Setting up sshd

**Here’s how to set up the OpenSSH server (`sshd`) on Windows 11 using Chocolatey.**

### 1. Prerequisites
- Run **PowerShell as Administrator**.
- Chocolatey must already be installed. If it isn’t:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2. Install OpenSSH with the server feature
The package is called `openssh`. Use the `/SSHServerFeature` parameter so it installs and configures the `sshd` service (and usually opens the firewall for port 22):

```powershell
choco install openssh -y --params '"/SSHServerFeature"'
```

Optional useful parameters:
- `/SSHServerPort:2222` — use a non-default port
- `/SSHAgentFeature` — also install/enable the SSH agent (often included automatically with the server feature)
- For the latest/prerelease build: add `--pre`

Example with a custom port:

```powershell
choco install openssh -y --params '"/SSHServerFeature /SSHServerPort:2222"'
```

### 3. Finish setup (if needed)
In many cases the package handles service installation and the firewall rule. If the service is not present or not running:

```powershell
# Go to the install folder (usually this path)
cd "C:\Program Files\OpenSSH-Win64"

# Install/register the service
.\install-sshd.ps1

# Set to start automatically and start it
Set-Service -Name sshd -StartupType Automatic
Start-Service sshd

# Confirm firewall rule (the package usually creates one)
Get-NetFirewallRule -Name *ssh* | Format-Table Name, Enabled, Direction, Action
```

If no rule exists:

```powershell
New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' `
  -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### 4. Verify
```powershell
Get-Service sshd
ssh localhost          # or ssh your-username@localhost
```

You should be able to log in with your Windows username and password (or key-based auth once configured).

## DO NOT do Step 5, if you are working with Jenkins

Jenkins cannot work with powershell

### 5. Optional configuration
- Config file location: `%ProgramData%\ssh\sshd_config`
- Default shell (e.g. PowerShell instead of `cmd`):

```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell `
  -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
```

Restart the service after config changes:

```powershell
Restart-Service sshd
```

That’s the complete Chocolatey-based flow for `sshd` on Windows 11.

# Configure SSH key authentication

**Here’s how to configure SSH public-key authentication** on the OpenSSH server you set up on Windows 11.

### 1. Generate a key pair (on the client machine)
Open PowerShell or Command Prompt and run:

```powershell
ssh-keygen -t ed25519 -C "your-email-or-comment"
```

- Press Enter to accept the default location (`C:\Users\<You>\.ssh\id_ed25519`).
- Optionally set a passphrase (recommended for security).

This creates:
- **Private key**: `id_ed25519` (keep this secret)
- **Public key**: `id_ed25519.pub`

(You can also use `-t ecdsa` or `-t rsa` if preferred.)

### 2. Copy the public key to the Windows SSH server
The location depends on whether the target Windows account is in the **Administrators** group.

#### A. Standard (non-Administrator) user
1. On the server, create the folder if needed:
   ```powershell
   mkdir $env:USERPROFILE\.ssh -Force
   ```
2. Create or edit the authorized keys file and paste the **contents** of the `.pub` file into it:
   ```powershell
   # Example: paste the public key content
   notepad $env:USERPROFILE\.ssh\authorized_keys
   ```
   Or append it from the client (if you can already log in with a password):
   ```powershell
   type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh username@windows-pc "mkdir -Force C:\Users\username\.ssh; Add-Content -Force C:\Users\username\.ssh\authorized_keys"
   ```

#### B. Administrator account (most common case)
By default, Windows OpenSSH uses a special file for Administrators:

1. On the server (run PowerShell **as Administrator**):
   ```powershell
   # Create the file if it doesn't exist and add the public key
   $pubKey = Get-Content "path\to\id_ed25519.pub"   # or paste it
   Add-Content -Force -Path "$env:ProgramData\ssh\administrators_authorized_keys" -Value $pubKey
   ```

2. **Set correct permissions** (critical – otherwise key auth will fail):
   ```powershell
   icacls.exe "$env:ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
   ```

   Only `SYSTEM` and `Administrators` should have access.

### 3. Enable public-key authentication in `sshd_config`
1. Open the config file as Administrator:
   ```powershell
   notepad C:\ProgramData\ssh\sshd_config
   ```

2. Make sure these lines are present and **not commented out**:
   ```
   PubkeyAuthentication yes
   ```

   (Optional but recommended for security after testing):
   ```
   PasswordAuthentication no
   ```

3. Save the file.

4. Restart the SSH service:
   ```powershell
   Restart-Service sshd
   ```

### 4. Test the connection
From the client:

```powershell
ssh username@windows-pc-ip-or-hostname
```

If you used a non-default private key location or name:

```powershell
ssh -i C:\path\to\id_ed25519 username@windows-pc-ip
```

You should log in without a password (or only with the key passphrase if you set one).

### 5. Optional: Use the SSH agent (client side)
To avoid entering the passphrase every time:

```powershell
# Start the agent and set it to automatic
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent

# Add your key
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

### Important notes for Windows
- **Administrators** always use `C:\ProgramData\ssh\administrators_authorized_keys` by default (controlled by a `Match Group administrators` block in `sshd_config`).
- File permissions must be strict — incorrect ACLs are the most common reason key authentication fails.
- After any change to `sshd_config` or the keys files, restart `sshd`.
- You can still keep password authentication enabled while testing (`PasswordAuthentication yes`).

Once everything works, you can disable password authentication for better security. Let me know if you run into any specific error messages!

# If things don't work still - From Copilot

Your new log tells me **two separate failures** are happening now — one for **public‑key auth**, and one for **process creation after password auth**. I’ll break them down cleanly and tell you exactly what fixes them.

## ✅ **Concise takeaway**

1. **Your public key is still being rejected** — now from `C:\Users\<user>\.ssh\authorized_keys` → This is a **permissions or encoding** problem.
    
2. After password login, Windows OpenSSH tries to spawn a shell using `CreateProcessAsUserW` → Error **1314 = “A required privilege is not held by the client.”** → This means your user **lacks SeAssignPrimaryTokenPrivilege or SeIncreaseQuotaPrivilege**.
    

Both issues must be fixed for SSH to work normally.

## 🧩 **Part 1 — Why your public key is still failing**

Your log:

Code

```
debug1: trying public key file C:\Users\<user>\.ssh\authorized_keys
Failed publickey for <user>
```

This means:

- The file **exists**
    
- The server **read it**
    
- The key was **rejected** (permissions or encoding)
    

Windows OpenSSH requires **UNIX‑style strict permissions**:

### 🔒 Required ACLs for `authorized_keys`

Only:

- SYSTEM — FullControl
    
- <user> — FullControl
    

Nothing else. No inheritance.

### ✔ Fix the ACLs

powershell

```
$path = "$env:USERPROFILE\.ssh\authorized_keys"
$acl = Get-Acl $path
$acl.SetAccessRuleProtection($true, $false)

$user = "$env:USERNAME"
$ruleUser = New-Object System.Security.AccessControl.FileSystemAccessRule($user,"FullControl","Allow")
$ruleSystem = New-Object System.Security.AccessControl.FileSystemAccessRule("SYSTEM","FullControl","Allow")

$acl.SetAccessRule($ruleUser)
$acl.SetAccessRule($ruleSystem)
$acl | Set-Acl
```

### ✔ Fix encoding (UTF‑8 no BOM)

If the file was ever edited in Notepad or PowerShell redirection, it may be UTF‑16.

powershell

```
$Utf8NoBom = New-Object System.Text.UTF8Encoding($False)
$content = Get-Content "$env:USERPROFILE\.ssh\authorized_keys"
[System.IO.File]::WriteAllLines("$env:USERPROFILE\.ssh\authorized_keys", $content, $Utf8NoBom)
```

### ✔ Ensure your key is actually in the file

Your public key must be **one line**, starting with:

Code

```
ssh-rsa AAAA...
```

## 🧩 **Part 2 — Why password login fails with error 1314**

Your log:

Code

```
Not running as SYSTEM: skipping loading user profile
CreateProcessAsUserW failed error:1314
fork of unprivileged child failed
```

This is **not** an SSH key problem. This is Windows refusing to create the user’s shell because the SSHD service account **does not have required privileges**.

### 🔥 Root cause

The **sshd service** is running as **LOCAL SERVICE** or **NETWORK SERVICE**, which _cannot_ call `CreateProcessAsUserW`.

### ✔ Fix: Run sshd as **LocalSystem**

This is the official Microsoft recommendation.

powershell

```
Stop-Service sshd
Set-Service -Name sshd -StartupType Automatic
sc.exe config sshd obj= "LocalSystem" type= own
Start-Service sshd
```

### ✔ Fix: Ensure privileges are assigned

LocalSystem already has:

- SeAssignPrimaryTokenPrivilege
    
- SeIncreaseQuotaPrivilege
    

If you run sshd under a custom account, you must manually grant these via Local Security Policy:

Code

```
secpol.msc → Local Policies → User Rights Assignment
```

Add the sshd service account to:

- **Replace a process level token**
    
- **Adjust memory quotas for a process**
    

## 🧪 **Checklist to fix your exact failure**

Each item is a Guided Link you can tap to continue:

- **Fix authorized_keys ACLs**
    
- **Fix UTF‑8 encoding**
    
- **Verify public key content**
    
- **Run sshd as LocalSystem**
    
- **Grant required privileges**
    

## 🧠 Non‑obvious insight

The message:

Code

```
Not running as SYSTEM: skipping loading user profile
```

is a **hard indicator** that sshd is running under the wrong account. Even if key auth succeeds, **you will still fail to spawn a shell** until sshd runs as LocalSystem.

## Want me to walk through your exact ACLs or sshd_config?

Tell me:

- **Check my ACLs**
    
- **Show my sshd_config**
    

I can pinpoint the exact line causing the failure.

# Problems (answered from Grok):

## 1: ___DON'T USE RSA keys___

## 1.5. how do I fix the public key on a windows 11 pro ssh server?

Yes. Since your SSH client is Jenkins and the target is **Windows 11 Pro**, the fix is slightly different from Linux.

The key detail is whether `amrobot` is a **local administrator** on the Windows 11 machine. Windows OpenSSH uses a different authorized-key file for administrator accounts. M![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Flearn.microsoft.com&sz=128)Microsoft Learn+1

### 1. Get the public key from Jenkins

On the Jenkins machine/container, you have this private key:

```text
/var/jenkins_home/.ssh/shuttle2-ed25519
```

Generate the corresponding public key:

```bash
ssh-keygen -y -f /var/jenkins_home/.ssh/shuttle2-ed25519 \
  > /var/jenkins_home/.ssh/shuttle2-ed25519.pub
```

Verify its fingerprint:

```bash
ssh-keygen -lf /var/jenkins_home/.ssh/shuttle2-ed25519.pub
```

You should get the fingerprint from your SSH log:

```text
SHA256:Bn2/xKnh1YBKHfMK9jv/XPnmc9HSvQr4HKe3Tx0cu6E
```

That confirms we're installing the **right public key**.

### 2. On Windows, determine whether `amrobot` is an administrator

Open **PowerShell as Administrator** on the Windows 11 machine:

```powershell
net user amrobot
```

Look for:

```text
Local Group Memberships
```

If you see `*Administrators`, use the **administrator procedure below**.

---

### If `amrobot` IS an administrator

This is probably the important part in your case.

Windows OpenSSH normally uses:

```text
C:\ProgramData\ssh\administrators_authorized_keys
```

instead of:

```text
C:\Users\amrobot\.ssh\authorized_keys
```

for administrator accounts. M![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Flearn.microsoft.com&sz=128)Microsoft Learn+1

On the Windows machine, open **PowerShell as Administrator**.

First create the directory/file if necessary:

```powershell
New-Item -ItemType Directory -Force C:\ProgramData\ssh
New-Item -ItemType File -Force C:\ProgramData\ssh\administrators_authorized_keys
```

Now you need to put the public key from Jenkins into that file.

The easiest method is to display the public key on Jenkins:

```bash
cat /var/jenkins_home/.ssh/shuttle2-ed25519.pub
```

It will look approximately like:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI.......
```

Copy the **entire single line**.

On Windows:

```powershell
notepad C:\ProgramData\ssh\administrators_authorized_keys
```

Paste the public key as **one line**, save, and close Notepad.

#### Fix the Windows permissions

This part is important. Microsoft specifies that `administrators_authorized_keys` should have permissions for `SYSTEM` and `Administrators`. M![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Flearn.microsoft.com&sz=128)Microsoft Learn+1

Run:

```powershell
icacls.exe C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
```

Check it:

```powershell
icacls.exe C:\ProgramData\ssh\administrators_authorized_keys
```

You should see entries for `Administrators` and `SYSTEM`.

Then restart SSH:

```powershell
Restart-Service sshd
```

---

### If `amrobot` is NOT an administrator

Then Windows should use:

```text
C:\Users\amrobot\.ssh\authorized_keys
```

Create the directory:

```powershell
New-Item -ItemType Directory -Force C:\Users\amrobot\.ssh
```

Then:

```powershell
notepad C:\Users\amrobot\.ssh\authorized_keys
```

Paste the **entire `ssh-ed25519 ...` public key from Jenkins** into that file.

Microsoft documents this as the standard location for non-administrator Windows users. M![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Flearn.microsoft.com&sz=128)Microsoft Learn

Then restart:

```powershell
Restart-Service sshd
```

---

### 3. Test from Jenkins

From the Jenkins container/machine, run:

```bash
ssh -vvv \
  -o IdentitiesOnly=yes \
  -i /var/jenkins_home/.ssh/shuttle2-ed25519 \
  amrobot@192.168.172.158
```

You want to see something like:

```text
Offering public key: /var/jenkins_home/.ssh/shuttle2-ed25519
Server accepts key
```

followed by successful authentication.

Your previous output stopped at:

```text
Offering public key: /var/jenkins_home/.ssh/shuttle2-ed25519
...
receive packet: type 51
Authentications that can continue: publickey,password,keyboard-interactive
```

After fixing the Windows authorized-key file, that should change to a successful public-key authentication.

### 4. If it still rejects the key

On Windows 11, check the SSH server configuration:

```powershell
notepad C:\ProgramData\ssh\sshd_config
```

Look for:

```text
PubkeyAuthentication yes
```

Also look for an `AuthorizedKeysFile` line. If it's commented out, the Windows defaults apply. Microsoft documents the Windows default as `.ssh/authorized_keys` for normal users and `%programdata%/ssh/administrators_authorized_keys` for administrators. M![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Flearn.microsoft.com&sz=128)Microsoft Learn

You can also validate the configuration before restarting:

```powershell
C:\Windows\System32\OpenSSH\sshd.exe -t
```

If that returns nothing, that's generally a good sign.

Then:

```powershell
Restart-Service sshd
```

#### One thing I'd check first in your situation

Because you're connecting as:

```text
amrobot@192.168.172.158
```

**check whether `amrobot` is a member of Administrators.**

If it is, don't put the key in:

```text
C:\Users\amrobot\.ssh\authorized_keys
```

Put it in:

```text
C:\ProgramData\ssh\administrators_authorized_keys
```

with the correct ACL. That's a very common reason for exactly the public-key rejection you're seeing on Windows OpenSSH. M![](https://www.google.com/s2/favicons?domain=https%3A%2F%2Flearn.microsoft.com&sz=128)Microsoft Learn+1

Microsoft's Windows OpenSSH key-based authentication guide

If you tell me whether **`amrobot` is an Administrator or standard user**, I can give you the exact PowerShell commands to fix it without changing anything unnecessary.

## 2: 

**Permission denied (publickey,keyboard-interactive)** means the server rejected both public-key authentication **and** password/keyboard-interactive authentication.

This is very common on Windows OpenSSH when the account is in the Administrators group or when permissions/`sshd_config` are not set correctly.

### Quick diagnosis checklist (run these on the **Windows server** as Administrator)

#### 1. Check whether the user is an Administrator
```powershell
net localgroup Administrators
```
If `amrse` is listed → the public key **must** go in the special admin file (see step 2).

#### 2. Correct location for the public key

**If the user is an Administrator** (most common case):
```powershell
# Create/edit the file
notepad C:\ProgramData\ssh\administrators_authorized_keys
```
Paste the **entire contents** of your client’s `.pub` file (one line starting with `ssh-ed25519` or `ssh-rsa`…).

Then fix permissions (critical):
```powershell
icacls.exe "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
```

**If the user is a normal (non-admin) user**:
```powershell
mkdir C:\Users\amrse\.ssh -Force
notepad C:\Users\amrse\.ssh\authorized_keys
```
Paste the public key, then set permissions so only the user + SYSTEM have access.

#### 3. Check / fix `sshd_config`
```powershell
notepad C:\ProgramData\ssh\sshd_config
```

Make sure these lines exist and are **not** commented:
```
PubkeyAuthentication yes
PasswordAuthentication yes          # temporarily keep this so you can still log in with password while testing
```

Look for this block (near the bottom) and either leave it or comment it out depending on what you want:

```
Match Group administrators
    AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

- Leave it enabled → keys for admins must be in `administrators_authorized_keys`.
- Comment both lines out → admins can use the normal `C:\Users\amrse\.ssh\authorized_keys`.

Save the file, then restart the service:
```powershell
Restart-Service sshd
```

#### 4. Temporary password login test
From the client try forcing password auth:
```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no amrse@HOSTNAME
```
If this works, the problem is only with the key setup.  
If this also fails, password authentication is disabled or the account has issues.

#### 5. Check the server logs for the exact reason
On the Windows machine:
```powershell
Get-Content C:\ProgramData\ssh\logs\sshd.log -Tail 50
```
or enable more verbose logging temporarily by adding to `sshd_config`:
```
LogLevel DEBUG3
```
Then restart `sshd` and try the connection again. Look for lines about “authorized keys”, “permission denied”, or “Failed to open file”.

#### 6. Client-side checks
- Make sure you are offering the correct private key:
  ```bash
  ssh -i ~/.ssh/id_ed25519 -v amrse@HOSTNAME
  ```
  The `-v` flag shows which keys are being tried.
- Confirm the public key on the server exactly matches the one corresponding to the private key you are using.

---

### Most frequent fixes that solve this error
1. Put the public key in `C:\ProgramData\ssh\administrators_authorized_keys` (because the account is an admin).
2. Run the exact `icacls` command above so only Administrators + SYSTEM have rights.
3. Restart `sshd`.
4. Temporarily keep `PasswordAuthentication yes` until key auth works.

After you make the changes, try the connection again and tell me:
- Whether `amrse` is in the Administrators group
- What the `sshd.log` shows for the failed attempt
- Whether password login currently works

I can then give the exact next command.

## 3:

The debug log gives a clear picture.

### What the log shows
- Username: **<user>**
- The account is in the **Administrators** group → SSH is correctly looking in:
  ```
  C:\ProgramData\ssh\administrators_authorized_keys
  ```
- It received this public key from the client:
  ```
  ED25519 SHA256:eRWsCGY...
  ```
- Result: **Failed publickey**

So the key is being offered, but the server does **not** accept it from `administrators_authorized_keys`.

### Fix it (run as Administrator on the Windows server)

1. **Check the current content of the file**
   ```powershell
   Get-Content C:\ProgramData\ssh\administrators_authorized_keys
   ```

2. **Make sure the exact public key is in that file**
   - On the client (the machine you’re connecting from), run:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     # or whatever key you are using
     ```
   - Copy the **entire line** (starts with `ssh-ed25519 ...`).

3. **Put it in the correct file on the server**
   ```powershell
   # Open the file
   notepad C:\ProgramData\ssh\administrators_authorized_keys
   ```
   - Paste the public key on its own line.
   - Save and close.

4. **Set the required permissions** (this is critical)
   ```powershell
   icacls "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
   ```

5. **Restart sshd** (or just stop the debug instance and start the service)
   ```powershell
   # If you are still running the debug sshd, press Ctrl+C first
   Restart-Service sshd
   ```

6. **Test again** from the client:
   ```bash
   ssh -v <user>@HOSTNAME
   ```

### Extra checks if it still fails
- Confirm the fingerprint matches:
  ```powershell
  # On server, after adding the key
  ssh-keygen -lf C:\ProgramData\ssh\administrators_authorized_keys
  ```
  The SHA256 should be exactly `eRWsCGY...`.

- Make sure there are no extra spaces, blank lines, or Windows line endings issues (the key must be a single clean line).

- Temporarily re-enable password auth for testing:
  In `C:\ProgramData\ssh\sshd_config` set:
  ```
  PasswordAuthentication yes
  ```
  Then restart sshd and try `ssh <user>@...` with the password.

Reply with the output of these two commands after you update the file:

```powershell
Get-Content C:\ProgramData\ssh\administrators_authorized_keys
ssh-keygen -lf C:\ProgramData\ssh\administrators_authorized_keys
```

and we’ll confirm it matches.

## 4:

On your Mac, open **Terminal** and run one of these:

### Quickest way (copies to clipboard)
```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

This puts the public key directly into your clipboard.  
Then go back to the Windows server and paste it into Notepad.

---

### Alternative ways

**Just display it so you can select & copy manually:**
```bash
cat ~/.ssh/id_ed25519.pub
```

**If you used a different key name:**
```bash
# Example for RSA key
pbcopy < ~/.ssh/id_rsa.pub

# Or any custom name
pbcopy < ~/.ssh/your_custom_key.pub
```

**List your available public keys first** (if you’re not sure which one):
```bash
ls -l ~/.ssh/*.pub
```

After running `pbcopy`, switch to the Windows machine, open the `administrators_authorized_keys` file in Notepad, and paste (`Ctrl + V`).

