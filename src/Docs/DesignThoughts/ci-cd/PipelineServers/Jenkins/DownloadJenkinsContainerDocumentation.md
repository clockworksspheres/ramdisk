# download the jenkins docker container with setup documentation please

(grok solutions in this document not tested)

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

# A few prompts later:

prompts:
* how to configure a jenkins pipeline from the command line please
* with python please?
* with argparse options please?

## Revealed the following:

Here's a practical **command-line Python script** that uses the `python-jenkins` library + **`argparse`** to create a Jenkins Pipeline job. You can run it like this:

```bash
python create_jenkins_pipeline.py --url http://localhost:8080 \
  --user admin \
  --token your-api-token-here \
  --job-name my-new-pipeline \
  --type inline \
  --script-path ./my-pipeline.groovy
```

Or for a Git-based pipeline:

```bash
python create_jenkins_pipeline.py --url http://jenkins.example.com \
  --user admin \
  --token 11abc123def... \
  --job-name backend-ci \
  --type scm \
  --repo https://github.com/your-org/backend.git \
  --branch main \
  --jenkinsfile Jenkinsfile
```

### Full script: `create_jenkins_pipeline.py`

```python
#!/usr/bin/env python3
"""
Create a Jenkins Pipeline job from the command line using python-jenkins + argparse.
Supports inline Pipeline script or Pipeline from SCM (Git).
"""

import argparse
import sys
import textwrap
import jenkins
from jenkins import JenkinsException


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Create a Jenkins Pipeline job via CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # Inline script
              %(prog)s --url http://localhost:8080 --user admin --token ABC123 \\
                --job-name test-inline --type inline --script "echo Hello from CLI!"

              # From Git (Jenkinsfile in root)
              %(prog)s --url http://jenkins --user admin --token XYZ \\
                --job-name my-app-ci --type scm \\
                --repo https://github.com/company/app.git --branch main

              # With custom Jenkinsfile path and credentials
              %(prog)s ... --jenkinsfile ci/Jenkinsfile --credentials-id git-token
        """)
    )

    # Required connection arguments
    conn = parser.add_argument_group("Jenkins connection")
    conn.add_argument("--url", required=True, help="Jenkins server URL (http://... or https://...)")
    conn.add_argument("--user", required=True, help="Jenkins username")
    conn.add_argument("--token", required=True, help="Jenkins API token (not password)")

    # Job definition
    job = parser.add_argument_group("Job details")
    job.add_argument("--job-name", required=True, help="Name of the new Pipeline job")
    job.add_argument("--description", default="Created via CLI script", help="Job description")

    # Pipeline type & config
    pipeline = parser.add_argument_group("Pipeline configuration")
    pipeline.add_argument("--type", required=True, choices=["inline", "scm"],
                          help="Pipeline type: 'inline' (script) or 'scm' (from Git)")
    
    # Inline mode
    inline = parser.add_argument_group("Inline Pipeline options (used when --type=inline)")
    inline.add_argument("--script", help="Pipeline script content (string)")
    inline.add_argument("--script-path", help="Path to .groovy/.jenkinsfile file to read as script")

    # SCM mode
    scm = parser.add_argument_group("SCM Pipeline options (used when --type=scm)")
    scm.add_argument("--repo", help="Git repository URL")
    scm.add_argument("--branch", default="main", help="Branch name (default: main)")
    scm.add_argument("--jenkinsfile", default="Jenkinsfile", help="Path to Jenkinsfile in repo")
    scm.add_argument("--credentials-id", default="", help="Jenkins credentials ID for Git (optional)")

    args = parser.parse_args()

    # Validation
    if args.type == "inline":
        if not (args.script or args.script_path):
            parser.error("--type inline requires --script or --script-path")
        if args.script and args.script_path:
            parser.error("Use either --script or --script-path, not both")
    elif args.type == "scm":
        if not args.repo:
            parser.error("--type scm requires --repo")

    return args


def get_pipeline_script(args):
    if args.script:
        return args.script
    if args.script_path:
        try:
            with open(args.script_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Script file not found: {args.script_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading script file: {e}", file=sys.stderr)
            sys.exit(1)
    return None  # shouldn't reach here due to validation


def build_inline_config(args, pipeline_script):
    return f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{args.description}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{pipeline_script.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""


def build_scm_config(args):
    credentials_xml = f"<credentialsId>{args.credentials_id}</credentialsId>" if args.credentials_id else ""
    
    return f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{args.description}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>{args.repo}</url>
          {credentials_xml}
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/{args.branch}</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>{args.jenkinsfile}</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""


def main():
    args = parse_arguments()

    try:
        server = jenkins.Jenkins(args.url, username=args.user, password=args.token)
        
        if server.job_exists(args.job_name):
            print(f"Job '{args.job_name}' already exists → skipping creation.")
            return

        if args.type == "inline":
            script = get_pipeline_script(args)
            config_xml = build_inline_config(args, script)
        else:  # scm
            config_xml = build_scm_config(args)

        server.create_job(args.job_name, config_xml)
        print(f"Success! Pipeline job '{args.job_name}' created.")
        print(f"→ Open: {args.url.rstrip('/')}/job/{args.job_name}")

    except JenkinsException as e:
        print(f"Jenkins error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Quick setup

1. Install dependency:
   ```bash
   pip install python-jenkins
   ```

2. Make the script executable (optional):
   ```bash
   chmod +x create_jenkins_pipeline.py
   ```

3. Run with `--help` to see full usage:
   ```bash
   ./create_jenkins_pipeline.py --help
   ```

Let me know if you'd like to add features like:

- Update/reconfigure existing job
- Multibranch Pipeline support
- Folder support (`folder/job-name`)
- Trigger build after creation
- Dry-run mode (print XML without creating)

Enjoy automating your Jenkins setup! 🚀

## Next prompt:  Run a jenkins pipeline in python with argparse please

Here's a practical **Python script** that uses `argparse` + the **`python-jenkins`** library to **trigger (run)** a Jenkins Pipeline (or any job) from the command line.

### Features included
- Connect to Jenkins via URL + auth (user + API token)
- Specify job name (supports folders: `folder/my-pipeline`)
- Optional: pass build **parameters** (very common for parameterized pipelines)
- Optional: wait & follow console output
- Help message + examples

### Installation

```bash
pip install python-jenkins
```

### Script: `run_jenkins_pipeline.py`

```python
#!/usr/bin/env python3
"""
Trigger (run) a Jenkins job / Pipeline from the command line.
Supports parameters and optional console following.

Examples:
  # Simple trigger
  python run_jenkins_pipeline.py --url http://localhost:8080 --user admin --token abc123def \
    --job my-pipeline

  # With parameters
  python run_jenkins_pipeline.py ... --job deploy-app \
    --param ENVIRONMENT=staging --param VERSION=1.2.3 --param DRY_RUN=true

  # Follow console output
  python run_jenkins_pipeline.py ... --follow
"""

import argparse
import sys
import time
import jenkins
from jenkins import JenkinsException


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Trigger a Jenkins job / Pipeline from CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1] if "Examples:" in __doc__ else ""
    )

    # Connection
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url", required=True, help="Jenkins base URL (http://... or https://...)")
    conn.add_argument("--user", required=True, help="Jenkins username")
    conn.add_argument("--token", required=True, help="Jenkins API token (not password)")

    # Job
    job_group = parser.add_argument_group("Job to trigger")
    job_group.add_argument("--job", required=True, help="Job name (supports folders: folder/my-pipeline)")
    job_group.add_argument("--token-build", dest="build_token",
                           help="Optional 'Trigger builds remotely' auth token (if enabled on job)")

    # Parameters & behavior
    behavior = parser.add_argument_group("Build options")
    behavior.add_argument("--param", action="append", metavar="KEY=VALUE",
                          help="Build parameter(s) in format KEY=VALUE (repeatable)")
    behavior.add_argument("--follow", action="store_true",
                          help="Wait and print console output until build finishes")
    behavior.add_argument("--timeout", type=int, default=1800,
                          help="Max seconds to wait when --follow is used (default: 1800)")

    return parser.parse_args()


def parse_params(param_list):
    """Convert --param KEY=VALUE strings into dict"""
    params = {}
    if param_list:
        for p in param_list:
            if '=' not in p:
                print(f"Invalid parameter format: {p} (use KEY=VALUE)", file=sys.stderr)
                sys.exit(1)
            key, value = p.split('=', 1)
            params[key.strip()] = value.strip()
    return params


def follow_console(server, build_number, job_name, timeout_sec):
    """Poll and print console output until build ends"""
    print(f"Following console output of {job_name} #{build_number} ... (Ctrl+C to stop watching)\n")
    
    last_offset = 0
    start_time = time.time()

    while time.time() - start_time < timeout_sec:
        try:
            result = server.get_build_console_output(job_name, build_number)
            if result and len(result) > last_offset:
                print(result[last_offset:], end='', flush=True)
                last_offset = len(result)

            info = server.get_build_info(job_name, build_number)
            if info['building'] is False:
                status = "SUCCESS" if info['result'] == "SUCCESS" else f"FAILED ({info['result']})"
                print(f"\n\nBuild finished → {status}")
                return info['result'] == "SUCCESS"
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("\nStopped watching (build continues on Jenkins).")
            return None
        except Exception as e:
            print(f"\nError while following: {e}", file=sys.stderr)
            return False

    print(f"\nTimeout ({timeout_sec}s) reached. Build still running.", file=sys.stderr)
    return False


def main():
    args = parse_arguments()

    try:
        server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

        if not server.job_exists(args.job):
            print(f"Error: Job '{args.job}' does not exist on {args.url}", file=sys.stderr)
            sys.exit(1)

        params = parse_params(args.param)

        print(f"Triggering {args.job} ...")
        if params:
            print(f"  Parameters: {params}")

        queue_id = server.build_job(
            args.job,
            parameters=params,
            token=args.build_token
        )

        # Get build number from queue (may take a moment)
        time.sleep(1.5)
        queue_info = server.get_queue_item(queue_id)
        if 'executable' not in queue_info or queue_info['executable'] is None:
            print("Build queued, but no number available yet. Check Jenkins UI.")
            sys.exit(0)

        build_number = queue_info['executable']['number']
        print(f"→ Build started: #{build_number}")
        print(f"→ View in browser: {args.url.rstrip('/')}/job/{args.job.replace('/', '/job/')}/{build_number}")

        if args.follow:
            success = follow_console(server, build_number, args.job, args.timeout)
            if success is False:
                sys.exit(1)   # non-zero exit if failed

    except JenkinsException as e:
        print(f"Jenkins API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Usage examples

```bash
# Basic trigger
python run_jenkins_pipeline.py --url http://jenkins:8080 --user roy --token 11f8a...xyz \
  --job backend/build-and-test

# With parameters + follow output
python run_jenkins_pipeline.py --url http://jenkins:8080 --user roy --token 11f8a...xyz \
  --job deploy \
  --param TARGET_ENV=production \
  --param APP_VERSION=4.1.2 \
  --param APPROVE=true \
  --follow

# If job has "Trigger builds remotely" token enabled
... --token-build MY_REMOTE_TOKEN
```

### Tips
- Get API token: Jenkins → your user → Configure → API Token
- For **parameterized pipelines**, define parameters in job config first
- `--follow` polls console every ~2s (lightweight)
- Works with **Pipeline**, Freestyle, Multi-branch, etc.

Let me know if you'd like to add features like:

- Wait for success/failure & exit code
- Trigger multiple jobs
- Choose specific branch/tag (for multibranch)
- Dry-run mode

Happy automating! 🚀

## Next prompt:  Create a node for a test machine in python with argparse please

Here's a clean, self-contained **Python script** using `argparse` + the **`python-jenkins`** library to **create a new permanent agent (node)** in Jenkins — ideal for a test machine.

This script supports the two most common launch methods in 2025–2026:

- **Launch agents via inbound TCP connection (JNLP)** — easiest for test machines (no SSH setup needed)
- **Launch agents via SSH** — more secure/production-like (requires credentials already in Jenkins)

### Prerequisites

```bash
pip install python-jenkins
```

Get your **Jenkins API token** (User → Configure → API Token).

### Script: `add_jenkins_test_node.py`

```python
#!/usr/bin/env python3
"""
Create a new permanent Jenkins agent (node) for a test machine via CLI.
Supports JNLP (inbound) and SSH launch methods.

Examples:
  # JNLP/inbound agent (easiest for testing)
  python add_jenkins_test_node.py --url http://localhost:8080 \
    --user admin --token 11abc123... \
    --name test-machine-01 --executors 2 --remote-fs /home/jenkins/agent \
    --labels "test linux docker" --description "Test VM #1"

  # SSH agent (requires credential already in Jenkins)
  python add_jenkins_test_node.py ... --method ssh \
    --host 192.168.1.150 --port 22 --credentials-id my-ssh-key \
    --jvm-options "-Xmx512m"
"""

import argparse
import sys
import jenkins
from jenkins import JenkinsException


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Add a new permanent Jenkins agent (node) for a test machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1] if "Examples:" in __doc__ else ""
    )

    # Connection
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url",      required=True, help="Jenkins URL (http://... or https://...)")
    conn.add_argument("--user",     required=True, help="Jenkins username")
    conn.add_argument("--token",    required=True, help="Jenkins API token")

    # Node basics
    node = parser.add_argument_group("Node basics (required)")
    node.add_argument("--name",        required=True,  help="Node name (e.g. test-machine-01)")
    node.add_argument("--description", default="",     help="Node description")
    node.add_argument("--executors",   type=int, default=2, help="Number of executors (default: 2)")
    node.add_argument("--remote-fs",   default="/home/jenkins/agent", help="Remote FS root (default: /home/jenkins/agent)")
    node.add_argument("--labels",      default="",     help="Space-separated labels (e.g. 'test linux docker')")

    # Launch method
    launch = parser.add_argument_group("Launch method")
    launch.add_argument("--method", choices=["jnlp", "ssh"], default="jnlp",
                        help="Launch method: jnlp (inbound/TCP) or ssh (default: jnlp)")
    
    # SSH-specific (only used when --method=ssh)
    ssh = parser.add_argument_group("SSH options (used when --method=ssh)")
    ssh.add_argument("--host",           help="Hostname/IP of the agent machine")
    ssh.add_argument("--port",           type=int, default=22, help="SSH port (default: 22)")
    ssh.add_argument("--credentials-id", help="Jenkins credentials ID for SSH (must exist)")
    ssh.add_argument("--jvm-options",    default="", help="JVM options for agent (e.g. '-Xmx1g')")

    args = parser.parse_args()

    # Basic validation
    if args.method == "ssh":
        if not all([args.host, args.credentials_id]):
            parser.error("--method ssh requires --host and --credentials-id")

    return args


def create_jnlp_node(server, args):
    """Create inbound (JNLP) agent – agent connects to controller"""
    params = {
        'port': 0,                    # 0 = random / auto
        'jnlpProtocol': True,
    }
    if args.jvm_options:
        params['jvmOptions'] = args.jvm_options

    server.create_node(
        name=args.name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labelString=args.labels.strip(),
        description=args.description,
        launcher='inbound',           # or JNLP4-connect
        launcher_params=params
    )


def create_ssh_node(server, args):
    """Create SSH-launched agent – controller connects to agent"""
    launcher_params = {
        'host': args.host,
        'port': str(args.port),
        'credentialsId': args.credentials_id,
        'jvmOptions': args.jvm_options or '',
        'javaPath': '',               # empty = use default
        'prefixStartSlaveCmd': '',
        'suffixStartSlaveCmd': '',
        'launchTimeoutSeconds': '60',
        'maxNumRetries': '10',
        'retryWaitTime': '10',
    }

    server.create_node(
        name=args.name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labelString=args.labels.strip(),
        description=args.description,
        launcher='ssh',
        launcher_params=launcher_params
    )


def main():
    args = parse_arguments()

    try:
        server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

        if server.node_exists(args.name):
            print(f"Node '{args.name}' already exists → skipping.", file=sys.stderr)
            sys.exit(0)

        print(f"Creating node '{args.name}' ({args.method.upper()} method)...")

        if args.method == "jnlp":
            create_jnlp_node(server, args)
        else:
            create_ssh_node(server, args)

        print("Success!")
        print(f"→ View node: {args.url.rstrip('/')}/computer/{args.name}/")
        
        if args.method == "jnlp":
            print("\nNext steps:")
            print("  1. Go to the node page")
            print("  2. Click 'Launch agent' or copy the secret / JNLP command")
            print("  3. Run the agent.jar on your test machine")

        elif args.method == "ssh":
            print("\nJenkins will attempt to connect automatically.")
            print("Make sure:")
            print(f"  • SSH daemon is running on {args.host}:{args.port}")
            print(f"  • Credential '{args.credentials_id}' is valid")
            print("  • Firewall allows inbound SSH")

    except JenkinsException as e:
        print(f"Jenkins error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Quick usage examples

**JNLP (recommended for quick test machine setup):**

```bash
python add_jenkins_test_node.py \
  --url http://jenkins:8080 \
  --user roy \
  --token your-api-token-here \
  --name test-linux-01 \
  --executors 4 \
  --labels "test python docker linux" \
  --description "My Ubuntu test VM"
```

**SSH (when you already have SSH keys/credentials in Jenkins):**

```bash
python add_jenkins_test_node.py \
  --url https://jenkins.company.com \
  --user roy \
  --token 11f8a... \
  --name build-agent-03 \
  --method ssh \
  --host 10.20.30.45 \
  --credentials-id ssh-jenkins@build-agent-03 \
  --executors 8 \
  --remote-fs /jenkins/workspace \
  --labels "fast linux amd64"
```

Let me know if you want:

- Cloud agents (Kubernetes, EC2, Azure…)
- Folder/cloud-specific nodes
- Delete/disable node commands
- Wait & check online status after creation

Happy scaling your Jenkins farm! 🚀

## Next Prompt:  How to create and install a ssh key pair into the jenkins server on the jenkins server in python with argparse please

Here's a practical **Python script** with `argparse` that does the following on/from your local machine (or any machine that can reach the Jenkins controller):

1. **Generates** a new SSH key pair (ed25519 recommended in 2025–2026, or RSA-4096 fallback)
2. **Adds** it to Jenkins as a **"SSH Username with private key"** credential via the REST API

This is the most common and secure pattern when you want Jenkins to SSH somewhere (e.g., to deploy, to connect to agents, to Git over SSH, etc.).

### Important notes before running

- The script **does not** place keys into `~/.ssh/` on the Jenkins controller — it stores the private key **inside Jenkins Credentials store** (encrypted).
- You need **admin** rights (or Credentials → Create permission) on Jenkins.
- Use a **strong passphrase** in production (script supports it).
- Run this script **locally** or in CI — **not** inside Jenkins (unless you really trust the build and want to create credentials from a pipeline).

### Requirements

```bash
pip install python-jenkins cryptography  # cryptography is used for key generation
```

### Script: `create_ssh_credential_for_jenkins.py`

```python
#!/usr/bin/env python3
"""
Generate a new SSH key pair and add it as "SSH Username with private key"
credential in Jenkins via the API.

Examples:
  python create_ssh_credential_for_jenkins.py \
    --url http://jenkins:8080 \
    --user admin \
    --token 11abc123def456... \
    --cred-id my-deploy-key-2026 \
    --username git \
    --description "Deployment key for prod servers" \
    --passphrase "my-very-secure-pass-2026"
"""

import argparse
import sys
import getpass
from datetime import datetime

import jenkins
from jenkins import JenkinsException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate SSH key pair and store it in Jenkins Credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1] if "Examples:" in __doc__ else ""
    )

    # Jenkins connection
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url",      required=True, help="Jenkins URL (http(s)://...)")
    conn.add_argument("--user",     required=True, help="Jenkins username (with credential create rights)")
    conn.add_argument("--token",    required=True, help="Jenkins API token")

    # Credential details
    cred = parser.add_argument_group("Credential details (required)")
    cred.add_argument("--cred-id",     required=True,  help="Unique credential ID (e.g. deploy-key-2026)")
    cred.add_argument("--username",    required=True,  help="SSH username (e.g. git, ubuntu, jenkins)")
    cred.add_argument("--description", default=f"SSH key created {datetime.now().strftime('%Y-%m-%d')}",
                       help="Credential description")
    cred.add_argument("--passphrase",  default=None,
                       help="Optional passphrase for the private key (prompted if not provided)")

    # Key options
    key = parser.add_argument_group("Key generation options")
    key.add_argument("--type", choices=["ed25519", "rsa"], default="ed25519",
                     help="Key type: ed25519 (recommended) or rsa (default: ed25519)")
    key.add_argument("--rsa-bits", type=int, default=4096,
                     help="RSA key size if --type=rsa (default: 4096)")

    args = parser.parse_args()

    if not args.passphrase:
        args.passphrase = getpass.getpass("Enter passphrase for private key (empty = no passphrase): ")

    return args


def generate_ssh_key(key_type: str, rsa_bits: int, passphrase: str | None) -> tuple[str, str]:
    """Generate SSH key pair and return (private_pem, public_openssh)"""
    if key_type == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
        encryption = serialization.BestAvailableEncryption(
            passphrase.encode() if passphrase else b""
        ) if passphrase else serialization.NoEncryption()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=encryption
        ).decode("utf-8")

        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        ).decode("utf-8").strip()

    elif key_type == "rsa":
        from cryptography.hazmat.primitives.asymmetric import rsa
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=rsa_bits,
            backend=default_backend()
        )
        encryption = serialization.BestAvailableEncryption(
            passphrase.encode() if passphrase else b""
        ) if passphrase else serialization.NoEncryption()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=encryption
        ).decode("utf-8")

        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        ).decode("utf-8").strip()

    else:
        raise ValueError("Unsupported key type")

    return private_pem, public_key + f"  {args.username}@{args.cred_id}"  # optional comment


def add_ssh_credential(server: jenkins.Jenkins, args, private_key_pem: str):
    """Add SSH Username with private key credential via Jenkins API"""
    xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>
  <scope>GLOBAL</scope>
  <id>{args.cred_id}</id>
  <description>{args.description}</description>
  <username>{args.username}</username>
  <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey>{private_key_pem.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</privateKey>
  </privateKeySource>
  <passphrase>{args.passphrase if args.passphrase else ""}</passphrase>
</com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>"""

    server.create_credential(
        store="system",          # global store
        domain="_",              # global domain
        credential_xml=xml
    )


def main():
    args = parse_arguments()

    try:
        server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

        print(f"Generating {args.type.upper()} SSH key pair...")
        private_pem, public_openssh = generate_ssh_key(
            args.type, args.rsa_bits, args.passphrase
        )

        print("\n→ Public key (add this to target servers / GitHub / GitLab):\n")
        print(public_openssh)
        print("\n" + "-"*60 + "\n")

        print(f"Adding credential '{args.cred_id}' to Jenkins...")
        add_ssh_credential(server, args, private_pem)

        print("\nSuccess!")
        print(f"→ Credential ID     : {args.cred_id}")
        print(f"→ Username          : {args.username}")
        print(f"→ Description       : {args.description}")
        print(f"→ Scope             : Global")
        print(f"→ Type              : SSH Username with private key")
        print(f"→ Passphrase set?   : {'Yes' if args.passphrase else 'No'}")
        print("\nYou can now use this credential in:")
        print("  • Git SCM (Pipeline from SCM)")
        print("  • Publish Over SSH plugin")
        print("  • SSH agents / nodes")
        print("  • sshagent step in Pipeline")
        print(f"→ View: {args.url.rstrip('/')}/credentials/store/system/domain/_/credential/{args.cred_id}/")

    except JenkinsException as e:
        print(f"Jenkins API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Quick usage examples

**No passphrase (development / testing):**

```bash
python create_ssh_credential_for_jenkins.py \
  --url http://localhost:8080 \
  --user admin \
  --token your-api-token-here \
  --cred-id test-deploy-key \
  --username git
```

**With passphrase (production):**

```bash
python create_ssh_credential_for_jenkins.py \
  --url https://jenkins.company.com \
  --user roy \
  --token 11f8a... \
  --cred-id prod-ssh-key-2026 \
  --username ubuntu \
  --description "Key for production servers" \
  --type ed25519
```

### What to do next?

1. Copy the **public key** printed by the script.
2. Add it to:
   - `~/.ssh/authorized_keys` on remote servers/agents
   - GitHub/GitLab deploy keys or user SSH keys
3. Use the credential ID in pipelines:
   ```groovy
   sshagent(credentials: ['prod-ssh-key-2026']) {
       sh 'ssh ubuntu@prod-server uptime'
   }
   ```

Let me know if you want:

- Store in a **folder/domain** credential store
- RSA instead of ed25519 by default
- Export private key to file as well (less secure)
- Bulk import from existing keys

Happy secure Jenkins automation! 🚀

## Next Prompt: please add examples in argparse epilog to python scripts

Here are updated versions of the previous Python scripts with **improved, realistic examples** added to the `epilog` of `argparse` (so they show nicely when the user runs `--help`).

I'll show the key part (the `ArgumentParser` setup with better `epilog`) for each script we've discussed. You can copy-paste these into your existing files.

### 1. Create Pipeline job (`create_jenkins_pipeline.py`)

```python
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Create a Jenkins Pipeline job via CLI (inline script or from Git)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # 1. Simple inline pipeline
              %(prog)s --url http://jenkins:8080 --user admin --token 11f8a9b... \\
                --job-name smoke-test --type inline \\
                --script "pipeline { agent any; stages { stage('Hello') { steps { echo 'Hi!' } } } }"

              # 2. Inline from file
              %(prog)s --url http://localhost:8080 --user roy --token ABC123... \\
                --job-name build-backend --type inline --script-path ./Jenkinsfile.simple

              # 3. Pipeline from Git (main branch)
              %(prog)s --url https://jenkins.company.com --user admin --token xyz... \\
                --job-name ci-frontend --type scm \\
                --repo https://github.com/company/web-ui.git --branch main

              # 4. With custom Jenkinsfile path + credentials
              %(prog)s ... --job-name deploy-prod --type scm \\
                --repo git@gitlab.company.com:ops/infra.git --jenkinsfile deploy/Jenkinsfile \\
                --credentials-id gitlab-ssh-deploy-key --branch release/2026
        """)
    )
    # ... rest of the arguments ...
```

### 2. Run / Trigger Pipeline (`run_jenkins_pipeline.py`)

```python
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Trigger (run) a Jenkins job or Pipeline from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # 1. Basic trigger (no parameters)
              %(prog)s --url http://jenkins:8080 --user roy --token 11abc... \\
                --job nightly-regression

              # 2. With build parameters
              %(prog)s --url https://ci.company.com --user admin --token xyz... \\
                --job deploy-service --follow \\
                --param ENVIRONMENT=staging --param VERSION=2.4.1 --param DRY_RUN=true

              # 3. Trigger remote build with authentication token + follow logs
              %(prog)s --url http://localhost:8080 --user dev --token abc123... \\
                --job release-candidate --token-build REMOTE_TRIGGER_KEY_2026 --follow

              # 4. Trigger in folder
              %(prog)s --url http://jenkins --user admin --token ... \\
                --job "DevTeam/mobile/android/build" --param BUILD_TYPE=debug
        """)
    )
    # ... rest of the arguments ...
```

### 3. Add Jenkins Node / Agent (`add_jenkins_test_node.py`)

```python
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Add a new permanent Jenkins agent (test machine / build node)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # 1. JNLP/inbound agent (easiest for laptops/VMs)
              %(prog)s --url http://jenkins:8080 --user admin --token 11f8a... \\
                --name test-ubuntu-01 --executors 4 --labels "test linux docker python" \\
                --description "Ubuntu 24.04 test VM"

              # 2. SSH agent (controller connects to machine)
              %(prog)s --url https://ci.company.com --user roy --token xyz... \\
                --name build-agent-05 --method ssh \\
                --host 10.20.30.45 --credentials-id ssh-jenkins@agent05 \\
                --executors 8 --labels "fast linux amd64 heavy"

              # 3. JNLP with custom JVM options
              %(prog)s --url http://localhost:8080 --user admin --token ... \\
                --name windows-test-02 --executors 2 --remote-fs "C:\\Jenkins" \\
                --labels "windows test dotnet" --jvm-options "-Xmx768m"
        """)
    )
    # ... rest of the arguments ...
```

### 4. Create & Add SSH Credential (`create_ssh_credential_for_jenkins.py`)

```python
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate new SSH key pair and store it in Jenkins Credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # 1. Quick ed25519 key – no passphrase (development)
              %(prog)s --url http://jenkins:8080 --user admin --token 11abc... \\
                --cred-id deploy-key-dev --username git

              # 2. Production key with passphrase
              %(prog)s --url https://ci.company.com --user roy --token xyz... \\
                --cred-id prod-ssh-2026 --username ubuntu \\
                --description "Key for production web servers" --passphrase

              # 3. RSA-4096 key for legacy systems
              %(prog)s --url http://jenkins --user admin --token ... \\
                --cred-id legacy-gitlab-key --username git \\
                --type rsa --rsa-bits 4096 --description "GitLab legacy SSH key"

              # 4. Minimal + folder credential store (advanced)
              # (Note: store/domain not yet in this script – extend if needed)
        """)
    )
    # ... rest of the arguments ...
```

### Quick tip – how to make examples look clean in --help

- Use `textwrap.dedent("""...""")` to remove common leading whitespace
- Use `%(prog)s` so the script name is inserted automatically
- Number the examples (1., 2., ...) for readability
- Use `\\` line continuation in shell examples so they copy-paste nicely

Would you like me to:

- Combine several of these into one multi-purpose Jenkins CLI tool?
- Add subcommands (using `argparse` subparsers)?
- Include examples with folder paths / multibranch pipelines?

Just let me know which direction you'd like to go next.

-----



