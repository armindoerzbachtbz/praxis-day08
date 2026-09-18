#!/usr/bin/env python3
import os
import re
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
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "ci_cd_tofu.yml"
INFRA_DIR = ROOT / "infra" / "praxisauftrag-4"
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


def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_yaml(path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as workflow_file:
        return yaml.load(workflow_file, Loader=yaml.BaseLoader) or {}


def flatten_runs(workflow):
    runs = []
    for job in (workflow.get("jobs") or {}).values():
        for step in job.get("steps", []) or []:
            if isinstance(step, dict) and "run" in step:
                runs.append(str(step["run"]))
    return "\n".join(runs)


def find_step_run(workflow, step_name):
    for job in (workflow.get("jobs") or {}).values():
        for step in job.get("steps", []) or []:
            if isinstance(step, dict) and step.get("name") == step_name:
                return str(step.get("run", ""))
    return ""


def check_praxisauftrag4():
    workflow_exists = WORKFLOW_PATH.exists()
    check(
        "Workflow .github/workflows/ci_cd_tofu.yml existiert",
        workflow_exists,
        "Erstelle oder repariere die Datei .github/workflows/ci_cd_tofu.yml.",
    )

    workflow = load_yaml(WORKFLOW_PATH)
    workflow_text = read_text(WORKFLOW_PATH)
    run_text = flatten_runs(workflow)
    tofu_apply_run = find_step_run(workflow, "OpenTofu apply")

    check(
        "OpenTofu Setup Action wird verwendet",
        "opentofu/setup-opentofu" in workflow_text,
        "Nutze opentofu/setup-opentofu@v1, damit tofu in GitHub Actions verfügbar ist.",
    )

    check(
        "OpenTofu init läuft im Ordner infra/praxisauftrag-4",
        "working-directory: infra/praxisauftrag-4" in workflow_text and re.search(r"\btofu init\b", run_text),
        "Führe tofu init mit working-directory: infra/praxisauftrag-4 aus.",
    )

    check(
        "OpenTofu apply wird automatisch ausgeführt",
        "tofu apply -auto-approve" in run_text,
        "Führe tofu apply -auto-approve in der Pipeline aus.",
    )

    check(
        "Public Key wird aus EC2_SSH_KEY abgeleitet",
        "ssh-keygen -y -f ~/.ssh/ec2_key > /tmp/techstyle_ec2.pub" in run_text,
        "Leite den Public Key mit ssh-keygen -y aus dem Private Key ab.",
    )

    check(
        "ssh_public_key_path wird an OpenTofu apply übergeben",
        '-var="ssh_public_key_path=/tmp/techstyle_ec2.pub"' in tofu_apply_run,
        "Übergib -var=\"ssh_public_key_path=/tmp/techstyle_ec2.pub\" an tofu apply.",
    )

    check(
        "EC2 Public IP wird aus tofu output gelesen",
        "tofu output -raw public_ip" in run_text,
        "Lies die EC2-IP mit tofu output -raw public_ip aus.",
    )

    check(
        "EC2 Host wird an spätere Steps weitergegeben",
        'echo "ec2_host=$EC2_HOST" >> "$GITHUB_OUTPUT"' in run_text
        or 'echo "EC2_HOST=$EC2_HOST" >> "$GITHUB_ENV"' in run_text,
        "Schreibe EC2_HOST nach GITHUB_OUTPUT oder GITHUB_ENV, damit spätere Steps ihn verwenden können.",
    )

    check(
        "Deploy-Script deploy_docker.sh wird ausgeführt",
        "./deploy_docker.sh" in run_text,
        "Starte nach tofu apply das Docker Deployment mit ./deploy_docker.sh.",
    )

    check(
        "Health Check verwendet Port 5001 und /api/products",
        "http://$EC2_HOST:5001/api/products" in run_text
        or "http://${EC2_HOST}:5001/api/products" in run_text,
        "Prüfe die App über http://$EC2_HOST:5001/api/products.",
    )

    check(
        "infra/praxisauftrag-4 ist vorhanden",
        INFRA_DIR.exists() and (INFRA_DIR / "main.tf").exists(),
        "Lege den Infrastrukturordner infra/praxisauftrag-4 mit main.tf an.",
    )

    main_tf = read_text(INFRA_DIR / "main.tf")
    variables_tf = read_text(INFRA_DIR / "variables.tf")
    check(
        "Terraform-Konfiguration definiert ssh_public_key_path",
        "ssh_public_key_path" in variables_tf and "ssh_authorized_key" in main_tf,
        "Die Infrastruktur muss den Public Key per Cloud-Init an die EC2-Instanz übergeben.",
    )


def main():
    if RESULTS_FILE:
        Path(RESULTS_FILE).write_text("", encoding="utf-8")

    check_praxisauftrag4()

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
