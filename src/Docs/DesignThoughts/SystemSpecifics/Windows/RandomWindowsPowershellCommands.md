
## Link like a unix ```ln -s```
``` powershell
New-Item -ItemType SymbolicLink -Path "Link" -Target "Target"
```

## Allow execution of a script

Be careful, this can get really insecure if not managed correctly.  Better to say "Y" than "A"

``` powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

## Adding something to the Windows PATH

``` powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64", [EnvironmentVariableTarget]::User)
```

## Creating a new directory

``` powershell
New-Item -Path ".\NewDirectory" -ItemType Directory -Force
```

