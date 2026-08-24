# Set Up Jenkins Adding Windows Agent


## Create a LOCAL new user

```
```

## Get ssh set up

Install openssh with chocolatey

``` powershell
choco install openssh
```

Enable powershell scripts to run for this powershell session

``` powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

Install the sshd service

``` powershell
Start-Service sshd
```

Enable the sshd service across reboots

``` powershell
Set-Service -Name sshd -StartupType 'Automatic'
```

Open the firewall to port 22 for sshd

NOTE!! Need to fix to the right sshd server...

``` powershell
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH SSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Program "C:\Windows\System32\OpenSSH\sshd.exe"
```

Check that port22 is open

``` powershell
netstat -nao | findstr ":22"
```

Edit the  ```%PROGRAMDATA%\ssh\sshd_config``` file and make sure the line ```PubkeyAuthentication yes``` is uncommented, and set to yes.

- **Handle Administrator Accounts**: By default, Windows forces administrator accounts to use a special key file location.
    
    - **Option A (Recommended for single-user)**: Comment out the last two lines of the file that look like this:
        
        ```
        #Match Group administrators
        #       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
        ```
        
        This allows administrators to use the standard user key file location.
        
    - **Option B (Strict Security)**: Leave those lines active. You must then place your key in `C:\ProgramData\ssh\administrators_authorized_keys` instead of your user folder.

``` powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
```

Restart the sshd server:

``` powershell
Restart-Service sshd
Get-Service sshd
```

## Install same version of jdk as on server

```
choco install microsoft-openjdk-21
```

## Set the default shell to powershell


## Get sudoers file set up properly

```
```

## 


