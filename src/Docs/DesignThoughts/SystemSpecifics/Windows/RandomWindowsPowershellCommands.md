
## Link like a unix ```ln -s```
``` powershell
New-Item -ItemType SymbolicLink -Path "Link" -Target "Target"
```

## Allow execution of a script

Be careful, this can get really insecure if not managed correctly.  Better to say "Y" than "A"

``` powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```