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


