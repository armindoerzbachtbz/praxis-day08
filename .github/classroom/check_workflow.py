#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import yaml


def find_root():
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".github").is_dir():
            return p
        p = p.parent
    return Path(__file__).resolve().parent

ROOT = find_root()
SONARQUBE_WORKFLOW = ROOT / ".github" / "workflows" / "build.yml"
RESULTS_FILE = os.environ.get("CLASSROOM_RESULTS")

PASS = 0
FAIL = 0


def record(status, description):
    if RESULTS_FILE:
        with open(RESULTS_FILE, "a", encoding="utf-8") as result_file:
            result_file.write(f"{status}\t{description}\n")


def check(description, condition, solution):
    global PASS, FAIL

    if condition:
        print(f"PASS: {description}")
        print(f"::notice title=PASS: {description}::Check erfolgreich bestanden")
        record("PASS", description)
        PASS += 1
    else:
        print(f"FAIL: {description}")
        print(f"::error title=FAIL: {description}::{solution}")
        record("FAIL", description)
        FAIL += 1


def load_workflow(path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as workflow_file:
        return yaml.load(workflow_file, Loader=yaml.BaseLoader) or {}


def get_steps(workflow):
    jobs = workflow.get("jobs", {})
    build_job = jobs.get("build", {})
    steps = build_job.get("steps", [])
    return steps if isinstance(steps, list) else []



def check_sonarqube_workflow():
    workflow_path = SONARQUBE_WORKFLOW
    if not workflow_path.exists():
        ci_path = ROOT / ".github" / "workflows" / "ci.yml"
        if ci_path.exists():
            workflow_path = ci_path

    workflow_exists = workflow_path.exists()
    check(
        "Workflow-Datei (sonarqube.yml oder ci.yml) existiert",
        workflow_exists,
        "Erstelle die Datei .github/workflows/sonarqube.yml.",
    )

    if not workflow_exists:
        workflow = {}
        workflow_text = ""
    else:
        workflow = load_workflow(workflow_path)
        workflow_text = workflow_path.read_text(encoding="utf-8")

    # 1. Trigger (push) und Branch (main) konfiguriert
    on_config = workflow.get("on", {})
    if isinstance(on_config, dict):
        has_push = "push" in on_config
    elif isinstance(on_config, list):
        has_push = "push" in on_config
    else:
        has_push = "push" in workflow_text

    has_main_branch = "main" in workflow_text
    check(
        "Workflow-Trigger (push) und Branch (main) konfiguriert",
        has_push and has_main_branch,
        "Konfiguriere 'on: push' für den Branch main.",
    )

    # 2. Job Definition auf ubuntu-latest
    jobs = workflow.get("jobs", {})
    has_jobs = isinstance(jobs, dict) and len(jobs) > 0
    has_ubuntu = "ubuntu-latest" in workflow_text
    check(
        "Job für SonarQube-Analyse auf ubuntu-latest definiert",
        has_jobs and has_ubuntu,
        "Definiere einen Job unter 'jobs:' mit 'runs-on: ubuntu-latest'.",
    )

    # 3. Git Checkout mit fetch-depth: 0
    has_checkout = "actions/checkout" in workflow_text
    has_fetch_depth = "fetch-depth" in workflow_text and ("0" in workflow_text)
    check(
        "Git-Checkout mit fetch-depth: 0 konfiguriert",
        has_checkout and has_fetch_depth,
        "Nutze actions/checkout mit 'fetch-depth: 0'.",
    )

    # 4. SonarSource/sonarqube-scan-action mit SONAR_TOKEN und SONAR_HOST_URL
    has_scan_action = (
        "SonarSource/sonarqube-scan-action" in workflow_text
        or "sonarqube-scan-action" in workflow_text
    )
    has_sonar_token = "SONAR_TOKEN" in workflow_text
    has_sonar_host_url = "SONAR_HOST_URL" in workflow_text
    check(
        "SonarQube Scan Action mit SONAR_TOKEN und SONAR_HOST_URL konfiguriert",
        has_scan_action and has_sonar_token and has_sonar_host_url,
        "Verwende SonarSource/sonarqube-scan-action mit SONAR_TOKEN und SONAR_HOST_URL.",
    )

    # 5. SonarSource/sonarqube-quality-gate-action konfiguriert
    has_qg_action = (
        "SonarSource/sonarqube-quality-gate-action" in workflow_text
        or "sonarqube-quality-gate-action" in workflow_text
    )
    check(
        "SonarQube Quality Gate Action konfiguriert",
        has_qg_action,
        "Verwende SonarSource/sonarqube-quality-gate-action im Workflow.",
    )

    # 6. File sonar-project.properties im Repo-Root existiert
    sonar_props_file = ROOT / "sonar-project.properties"
    props_exists = sonar_props_file.exists()
    check(
        "Datei sonar-project.properties existiert im Repo-Root",
        props_exists,
        "Erstelle die Datei sonar-project.properties im Projekt-Root-Verzeichnis.",
    )

    # 7. sonar-project.properties enthält richtigem Inhalt (sonar.projectKey=techstyle)
    props_valid = False
    if props_exists:
        props_content = sonar_props_file.read_text(encoding="utf-8")
        props_valid = "sonar.projectKey=techstyle" in props_content
    check(
        "sonar-project.properties enthält sonar.projectKey=techstyle",
        props_valid,
        "Stelle sicher, dass sonar-project.properties den Eintrag 'sonar.projectKey=techstyle' enthält.",
    )
    


def main():
    if RESULTS_FILE:
        Path(RESULTS_FILE).write_text("", encoding="utf-8")

    check_sonarqube_workflow()

    print("")
    print("-----------------------------------------")
    print("Zusammenfassung")
    print("-----------------------------------------")
    print(f"Erfüllt: {PASS} Kriterien")
    print(f"Offen:   {FAIL} Kriterien")
    print("-----------------------------------------")

    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
