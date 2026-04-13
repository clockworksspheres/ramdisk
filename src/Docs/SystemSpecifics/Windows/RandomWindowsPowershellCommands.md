
## Link like a unix ```ln -s```
``` powershell
New-Item -ItemType SymbolicLink -Path "Link" -Target "Target"
```

## Allow execution of a script

Be careful, this can get really insecure if not managed correctly.  Better to say "Y" than "A".

``` powershell
Set-ExecutionPolicy Bypass -Scope Process
```

The following command is valid for only the current powershell session.

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

# References:

## Powershell references:

### Powershell for Beginners A Step-by-Step Guide 
https://www.amazon.com/dp/B0DSGG27G1/

### Online powershell devops community non-profit
https://powershell.org/

### Bertram, A. (2020). _PowerShell for Sysadmins: Workflow Automation Made Easy_. No Starch Press.

### Jones, D., & Hicks, J. (2013). _Learn Windows PowerShell in a Month of Lunches_. Manning Pubns Co.

### Dent, C. (2024). _Mastering PowerShell Scripting: Automate repetitive tasks and simplify complex administrative tasks using PowerShell_. Packt Publishing.

