# Installing Jenkins Agent on macOS

prompt on chatgpt 26-01-05 (if later, try the prompt again to get better/newer info)

```
install macos jenkins agent
```

---

Below is a **practical, step-by-step guide to installing and running a Jenkins agent on macOS**, covering the most common and reliable setup (SSH + Java). This works for Intel and Apple Silicon Macs.

---

## 1. Prerequisites on macOS

### ✅ Install Java (required)

Jenkins agents require Java (typically Java 11 or 17).

Check if Java exists:

```bash
java -version
```

If not installed, install via Homebrew:

```bash
brew install openjdk@17
```

Link it:

```bash
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk \
  /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

Verify:

```bash
java -version
```

---

### ✅ Install Homebrew (if needed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 2. Create a Jenkins Agent User (recommended)

```bash
sudo sysadminctl -addUser jenkins \
  -password "strong-password" \
  -home /Users/jenkins \
  -admin
```

Switch to it:

```bash
su - jenkins
```

---

## 3. Enable SSH Access on macOS

Jenkins commonly connects via SSH.

### Enable Remote Login

```bash
sudo systemsetup -setremotelogin on
```

Verify:

```bash
ssh localhost
```

---

## 4. Configure the Jenkins Controller

On the **Jenkins controller UI**:

1. **Manage Jenkins → Nodes → New Node**
2. Node name: `macos-agent`
3. Type: **Permanent Agent**

### Node configuration

| Setting               | Value                                       |
| --------------------- | ------------------------------------------- |
| Remote root directory | `/Users/jenkins/jenkins-agent`              |
| Launch method         | **Launch agents via SSH**                   |
| Host                  | macOS IP or hostname                        |
| Credentials           | SSH key or password                         |
| JavaPath              | (optional) `/usr/bin/java` or Homebrew path |
| Labels                | `macos`                                     |
| Usage                 | Use this node as much as possible           |

Save.

---

## 5. Set Up SSH Credentials (Recommended: SSH Key)


```bash
ssh-keygen -t ed25519 -f ~/.ssh/jenkins_macos_agent -C "useremail"
```

Copy key to macOS agent:

```bash
ssh-copy-id jenkins@mac-agent-host
```

Test:

```bash
ssh jenkins@mac-agent-host
```

---

## 6. First Agent Launch

When saved, Jenkins will:

* SSH into macOS
* Copy `agent.jar`
* Start the agent automatically

You should see **“Connected”** in the node status.

---

## 7. (Optional) Run Agent Manually with JNLP

If SSH is not allowed:

```bash
curl -O https://jenkins.example.com/jnlpJars/agent.jar
java -jar agent.jar \
  -url https://jenkins.example.com \
  -name macos-agent \
  -workDir ~/jenkins-agent
```

---

## 8. Run Agent as a macOS LaunchDaemon (Auto-start)

Create plist:

```bash
sudo nano /Library/LaunchDaemons/com.jenkins.agent.plist
```

Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.jenkins.agent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/java</string>
    <string>-jar</string>
    <string>/Users/jenkins/agent.jar</string>
    <string>-jnlpUrl</string>
    <string>https://jenkins.example.com/computer/macos-agent/jenkins-agent.jnlp</string>
    <string>-secret</string>
    <string>SECRET</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>UserName</key>
  <string>jenkins</string>
</dict>
</plist>
```

Load it:

```bash
sudo launchctl load /Library/LaunchDaemons/com.jenkins.agent.plist
```

---

## 9. Verify from Jenkins Pipeline

```groovy
pipeline {
  agent { label 'macos' }
  stages {
    stage('Test') {
      steps {
        sh 'sw_vers'
        sh 'uname -m'
      }
    }
  }
}
```

---

## 10. Common macOS Issues & Fixes

### ❌ “java not found”

```bash
which java
/usr/libexec/java_home -V
```

### ❌ Permission denied

```bash
sudo chown -R jenkins:staff /Users/jenkins
```

### ❌ Keychain / codesign issues (Xcode builds)

```bash
security unlock-keychain
```

---

## Summary

✔ Java installed
✔ SSH enabled
✔ Jenkins node configured
✔ Agent connects automatically
✔ macOS builds ready

---

If you want, I can also help with:

* **Apple Silicon vs Intel quirks**
* **Xcode / iOS signing on Jenkins agents**
* **Running Jenkins agent inside a macOS VM**
* **Hardening SSH & credentials**

Just tell me your Jenkins version and how you plan to use the macOS agent.



