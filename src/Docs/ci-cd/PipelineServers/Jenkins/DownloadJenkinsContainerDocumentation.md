# download the jenkins docker container with setup documentation

(Some grok solutions in this document not tested)

## The above was the prompt to grok.com, which revealed the following:

Here’s how to download (pull) and set up the official **Jenkins** Docker container, based on the current official recommendations (as of 2026).

The official image is maintained at: **https://hub.docker.com/r/jenkins/jenkins**

The recommended version for most users is the **LTS** (Long Term Support) release — stable and production-ready.

### Step 1: Make sure Docker is installed
Run this to verify:
```bash
docker --version
```
If not installed → https://docs.docker.com/get-docker/

### Step 2: Pull (download) the Jenkins image
Use one of these commands in your terminal:

- **Recommended (latest LTS, usually on recent JDK)**  
  ```bash
  docker pull jenkins/jenkins:lts
  ```

- **Explicit recent LTS with specific JDK** (very common in 2025–2026)  
  ```bash
  docker pull jenkins/jenkins:lts-jdk21
  ```
  or
  ```bash
  docker pull jenkins/jenkins:lts-jdk17
  ```

- **Latest weekly build** (not recommended for production)  
  ```bash
  docker pull jenkins/jenkins:latest
  ```

After pulling, verify:
```bash
docker images | grep jenkins
```

### Step 3: Run Jenkins (most common / recommended way)

#### To start the container:

```
docker start jenkins
```

#### To Download and run the container:  

This command gives you persistence + the two important ports:

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --restart unless-stopped \
  jenkins/jenkins:lts-jdk21
```

What each part means:

- `-d` → run in background
- `--name jenkins` → easy name to reference later
- `-p 8080:8080` → web UI (http://localhost:8080)
- `-p 50000:50000` → agent/master communication port (needed for distributed builds)
- `-v jenkins_home:/var/jenkins_home` → **very important** — saves all jobs, plugins, config outside the container
- `--restart unless-stopped` → auto-restart on boot/crash (except manual stop)
- You can swap `:lts-jdk21` for whichever tag you pulled

This downloads as well as running the container.  

### Step 4: Initial setup (very important!)
1. Wait ~30–90 seconds for startup
2. Open in browser: **http://localhost:8080** (or your-server-ip:8080)
3. Get the initial admin password:
   ```bash
   docker logs jenkins
   ```
   or
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
   → copy the long hex string

4. Paste it into the browser → continue setup wizard
   - Install suggested plugins (recommended for beginners)
   - Create first admin user
   - Instance configuration (usually leave default)
   - You're done — welcome to Jenkins!

### Quick cheat-sheet commands

Stop / start / restart:
```bash
docker stop jenkins
docker start jenkins
docker restart jenkins
```

See logs:
```bash
docker logs -f jenkins
```

Enter container (debug / manual plugin install / etc.):
```bash
docker exec -it -u root jenkins bash
```

Remove container (if you want to start fresh — **data is safe in volume**):
```bash
docker rm -f jenkins
```

### Official documentation (best & most up-to-date source)
- Main Docker install guide → https://www.jenkins.io/doc/book/installing/docker/
- GitHub repo with detailed README → https://github.com/jenkinsci/docker
- All available tags → https://hub.docker.com/r/jenkins/jenkins/tags

Let me know if you want the docker-compose version, how to run Jenkins with Docker-in-Docker (DinD), Blue Ocean pre-installed image, or anything else!


## Project one can use to manage Jenkins pipelines, nodes and installing an ssh key into the Jenkins Server.

https://github.com/clockworksspheres/jenkinsTools.git

## For managing local VMs for cross platform projects on macOS and Windows

https://github.com/clockworksspheres/vmm.git

On macOS, works with the following hypervisors currently:

* UTM
* VMware Fusion
* Oracle VirtualBox

On Windows, designed for the following hypervisors currently:

* HyperV
* VMware Workstation
* Oracle Virtualbox
