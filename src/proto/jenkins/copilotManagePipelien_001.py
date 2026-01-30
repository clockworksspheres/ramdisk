#!/usr/bin/env python3
import argparse
import jenkins
import xml.etree.ElementTree as ET
import sys
from typing import Dict, List, Optional

# -----------------------------
# Helpers for XML construction
# -----------------------------

def _elem(tag: str, text: Optional[str] = None, attrib: Optional[Dict[str, str]] = None):
    e = ET.Element(tag, attrib or {})
    if text is not None:
        e.text = text
    return e

def _add_child(parent: ET.Element, tag: str, text: Optional[str] = None, attrib: Optional[Dict[str, str]] = None):
    child = ET.SubElement(parent, tag, attrib or {})
    if text is not None:
        child.text = text
    return child

def pretty_xml(element: ET.Element) -> str:
    return ET.tostring(element, encoding="unicode")

# -----------------------------------
# Jenkins job XML generator
# -----------------------------------

def generate_pipeline_job_xml(
    job_name: str,
    repo_url: str,
    branch: str,
    script_path: str,
    downstream_jobs: Optional[List[str]] = None,
    credentials_id: Optional[str] = None,
) -> str:
    root = _elem("flow-definition", {"plugin": "workflow-job"})
    _add_child(root, "description", f"Pipeline for {job_name} in monorepo")
    _add_child(root, "keepDependencies", "false")

    definition = _add_child(root, "definition", attrib={
        "class": "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition",
        "plugin": "workflow-cps"
    })

    scm = _add_child(definition, "scm", attrib={
        "class": "hudson.plugins.git.GitSCM",
        "plugin": "git"
    })
    _add_child(scm, "configVersion", "2")
    user_remote_configs = _add_child(scm, "userRemoteConfigs")
    urc = _add_child(user_remote_configs, "hudson.plugins.git.UserRemoteConfig")
    _add_child(urc, "url", repo_url)
    if credentials_id:
        _add_child(urc, "credentialsId", credentials_id)

    branches = _add_child(scm, "branches")
    branch_spec = _add_child(branches, "hudson.plugins.git.BranchSpec")
    _add_child(branch_spec, "name", branch)

    _add_child(scm, "doGenerateSubmoduleConfigurations", "false")
    _add_child(scm, "submoduleCfg", attrib={"class": "list"})
    _add_child(scm, "extensions")

    _add_child(definition, "scriptPath", script_path)
    _add_child(definition, "lightweight", "true")

    _add_child(root, "disabled", "false")

    properties = _add_child(root, "properties")
    if downstream_jobs:
        build_trigger = _add_child(properties, "hudson.plugins.parameterizedtrigger.BuildTrigger")
        configs = _add_child(build_trigger, "configs")
        for dj in downstream_jobs:
            config = _add_child(configs, "hudson.plugins.parameterizedtrigger.BuildTriggerConfig")
            _add_child(config, "configs", attrib={"class": "empty-list"})
            _add_child(config, "projects", dj)
            _add_child(config, "condition", "SUCCESS")
            _add_child(config, "triggerWithNoParameters", "true")

    return pretty_xml(root)

# -----------------------------------
# Pipeline definitions
# -----------------------------------

def pipeline_service_a(args):
    job_name = f"{args.prefix}-service-a"
    xml = generate_pipeline_job_xml(
        job_name=job_name,
        repo_url=args.repo_url,
        branch=args.branch,
        script_path="services/service-a/Jenkinsfile",
        downstream_jobs=[f"{args.prefix}-service-b"] if args.chain else None,
        credentials_id=args.credentials_id,
    )
    return job_name, xml

def pipeline_service_b(args):
    job_name = f"{args.prefix}-service-b"
    xml = generate_pipeline_job_xml(
        job_name=job_name,
        repo_url=args.repo_url,
        branch=args.branch,
        script_path="services/service-b/Jenkinsfile",
        downstream_jobs=[f"{args.prefix}-service-c"] if args.chain else None,
        credentials_id=args.credentials_id,
    )
    return job_name, xml

def pipeline_service_c(args):
    job_name = f"{args.prefix}-service-c"
    xml = generate_pipeline_job_xml(
        job_name=job_name,
        repo_url=args.repo_url,
        branch=args.branch,
        script_path="services/service-c/Jenkinsfile",
        downstream_jobs=None,
        credentials_id=args.credentials_id,
    )
    return job_name, xml

PIPELINES = {
    "service-a": pipeline_service_a,
    "service-b": pipeline_service_b,
    "service-c": pipeline_service_c,
}

# -----------------------------------
# Jenkins operations
# -----------------------------------

def ensure_job(server: jenkins.Jenkins, job_name: str, xml: str, overwrite: bool = True, dry_run: bool = False):
    if dry_run:
        print(f"\n--- DRY RUN: Job {job_name} ---\n{xml}\n")
        return
    try:
        server.get_job_config(job_name)
        if overwrite:
            server.reconfig_job(job_name, xml)
            print(f"Updated job: {job_name}")
        else:
            print(f"Job exists, skipping: {job_name}")
    except jenkins.NotFoundException:
        server.create_job(job_name, xml)
        print(f"Created job: {job_name}")

def trigger_build(server: jenkins.Jenkins, job_name: str, params: Optional[Dict] = None, dry_run: bool = False):
    if dry_run:
        print(f"--- DRY RUN: Would trigger build for {job_name} ---")
        return
    server.build_job(job_name, parameters=params or {})
    print(f"Triggered build: {job_name}")

# -----------------------------------
# CLI
# -----------------------------------

def parse_args():
    epilog_text = """Examples:
  Create all pipelines and chain them:
    manage_pipelines.py --jenkins-url https://jenkins.example.com --username user --api-token token \\
      --repo-url https://github.com/org/monorepo.git --branch '*/main' --credentials-id git-creds --prefix mono --chain

  Dry run (print XML only, no Jenkins calls):
    manage_pipelines.py --jenkins-url https://jenkins.example.com --username user --api-token token \\
      --repo-url https://github.com/org/monorepo.git --dry-run

  Trigger service-a after creation:
    manage_pipelines.py --jenkins-url https://jenkins.example.com --username user --api-token token \\
      --repo-url https://github.com/org/monorepo.git --trigger service-a
"""
    p = argparse.ArgumentParser(
        description="Manage Jenkins pipelines for a monorepo.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--jenkins-url", required=True, help="Jenkins base URL")
    p.add_argument("--username", required=True, help="Jenkins username")
    p.add_argument("--api-token", required=True, help="Jenkins API token")
    p.add_argument("--repo-url", required=True, help="Git repository URL")
    p.add_argument("--branch", default="*/main", help="Git branch spec (e.g., */main)")
    p.add_argument("--credentials-id", help="Jenkins credentialsId for Git SCM")
    p.add_argument("--prefix", default="mono", help="Job name prefix")
    p.add_argument("--pipelines", nargs="+", choices=list(PIPELINES.keys()), default=list(PIPELINES.keys()),
                   help="Which pipelines to create/update")
    p.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing jobs")
    p.add_argument("--chain", action="store_true", help="Configure downstream triggers to chain pipelines")
    p.add_argument("--trigger", choices=list(PIPELINES.keys()), help="Trigger a specific pipeline after creation")
    p.add_argument("--dry-run", action="store_true", help="Print XML instead of creating jobs")
    return p.parse_args()

def main():
    args = parse_args()
    server = None
    if not args.dry_run:
        server = jenkins.Jenkins(args.jenkins_url, username=args.username, password=args.api_token)

    created_jobs = []
    for name in args.pipelines:
        job_name, xml = PIPELINES[name](args)
        ensure_job(server, job_name, xml, overwrite=not args.no_overwrite, dry_run=args.dry_run)
        created_jobs.append(job_name)

    if args.trigger:
        trigger_build(server, f"{args.prefix}-{args.trigger}", dry_run=args.dry_run)

    print("Done.")
    print("Jobs:", ", ".join(created_jobs))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

