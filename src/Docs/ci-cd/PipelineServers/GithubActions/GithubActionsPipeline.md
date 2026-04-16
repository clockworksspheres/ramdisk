# Github Actions Pipeline

Github Actions can use matrix methods to orchestrate multiple pipelines. Testing involves github actions runners on each of multiple operating systems.  This is more complex than using Jenkins, so Jenkins is the current testing orchestration service.

In the future, the two may be set to work together, to report testing results to github.

Also, one may be able to use ansible to set up github actions runners, and register these runners with github.  Possible github repos that can facilitate this include:

https://github.com/MonolithProjects/ansible-github_actions_runner

https://github.com/compscidr/ansible-github-runner

# References

[# CI/CD Pipeline for PyInstaller on GitHub Actions for Windows](https://ragug.medium.com/ci-cd-pipeline-for-pyinstaller-on-github-actions-for-windows-7f8274349278)

[# Feature: An official GitHub Action to build PyInstaller executables](https://github.com/pyinstaller/pyinstaller/issues/6296)

[# PyInstaller-Action-Windows](https://github.com/marketplace/actions/pyinstaller-windows)

[# Build a multi OS Python app in the cloud: PyInstaller on GitHub Actions](https://data-dive.com/multi-os-deployment-in-cloud-using-pyinstaller-and-github-actions/)

[# GitHub Actions Runner](https://github.com/MonolithProjects/ansible-github_actions_runner)

[# ansible-github-runner](https://github.com/compscidr/ansible-github-runner)

[# How to run any action on all runners at the same time? #50456](https://github.com/orgs/community/discussions/50456)

[# Self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)

[# Self-hosted runners](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners)