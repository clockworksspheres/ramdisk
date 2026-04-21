s# Set Up Jenkins Adding Windows Agent


## Create a new user

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

## Install same version of jdk as on server

```
choco install microsoft-openjdk-21
```

## Get sudoers file set up properly

```
```

## 


