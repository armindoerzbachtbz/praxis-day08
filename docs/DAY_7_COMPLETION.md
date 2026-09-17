# Day 7 Completion — Test Automation & SonarQube

## Scope

Day 7 has two halves: (1) standing up a **SonarQube Community Edition server**
on an EC2 VM via Terraform + Docker Compose, and (2) **wiring the TechStyle
CI pipeline** to scan against it and enforce the Quality Gate.

Part 1 (the EC2/Terraform infrastructure) is deliberately **not** part of this
repo — the course's own model solution puts that Infrastructure-as-Code in the
separate `musterloesungen-praxisauftraege` repo (`tag07/sonarqube-vm.tf`,
`tag07/cloud-init.yml`, `tag07/docker-compose.yml`), not in the application
repo, and provisioning it means real, billable AWS resources via a
Learner-Lab account. That's a manual, credentialed step for the
student/team, not something to run unattended from here. This completion
covers Part 2 in full: everything on the TechStyle side needed to consume a
running SonarQube instance.

## What Was Completed

### Task 1: SonarQube Scanner Configuration ✅
- Added `sonar-project.properties` at repo root:
  - `sonar.projectKey=techstyle`, `sonar.sources=.` with exclusions for
    `.venv/`, `static/`, `templates/`, `tests/`, `docs/`, build output
  - `sonar.tests=tests`, `sonar.python.version=3.11`
  - `sonar.python.coverage.reportPaths=coverage.xml` so SonarQube shows real
    line coverage instead of 0%
  - `sonar.qualitygate.wait=true` (per the Tag 07 hint) — this makes the
    scan **step itself fail** if the Quality Gate is red, which is what
    actually breaks the pipeline (a green dashboard with a passing CI run
    would defeat the point).

### Task 2: Coverage Reporting ✅
- Added `pytest-cov` to `requirements.txt`.
- `ci.yml`'s `test` job now runs
  `pytest tests/ -v --tb=short --cov=app --cov-report=xml --cov-report=term`
  and uploads `coverage.xml` as a job artifact (`coverage-report`), so the
  SonarQube job can consume it without re-running the test suite.

### Task 3: SonarQube Job in the Pipeline ✅
- Added a `sonarqube` job to `.github/workflows/ci.yml`:
  - `needs: test` — only scans code that already passed lint + tests
  - `fetch-depth: 0` checkout (SonarQube wants full git history for blame
    info / new-code detection)
  - Downloads the `coverage-report` artifact from the `test` job
  - Runs `SonarSource/sonarqube-scan-action@v4` against `SONAR_HOST_URL` /
    `SONAR_TOKEN` (repo secrets)
  - **Guarded with `if: ${{ secrets.SONAR_HOST_URL != '' }}`**: until a team
    has actually provisioned their EC2 SonarQube instance and added the
    secrets, this job skips cleanly instead of failing every push. This
    keeps `lint`/`test`/`build` working for everyone regardless of whether
    their SonarQube server currently exists.
  - `build` still only depends on `test`, not on `sonarqube` — the artifact
    build stays independent of the (optional, infra-gated) quality gate so
    the existing Day 6 artifact pipeline never regresses.

## Manual Setup Required (once the EC2 SonarQube server is running)

1. Provision the server from `musterloesungen-praxisauftraege/tag07/`
   (`terraform init && terraform apply`) — see that repo's `README.md`.
2. Log into `http://<ELASTIC-IP>:9000` (`admin`/`admin`), change the password.
3. **Create a local project** for `techstyle`, generate a token
   (My Account → Security → Generate Token).
4. In the TechStyle GitHub repo: **Settings → Secrets and variables →
   Actions**, add:
   - `SONAR_HOST_URL` = `http://<ELASTIC-IP>:9000`
   - `SONAR_TOKEN` = the generated token
5. Push to a `day_*`/`main` branch — the `sonarqube` job now runs and blocks
   the pipeline if the Quality Gate fails.
6. When done: `terraform destroy` in the infra repo to avoid leaving the EC2
   instance running.

## Files Added / Changed

| File | Change |
|------|--------|
| `sonar-project.properties` | New — SonarQube scanner configuration |
| `requirements.txt` | Changed — added `pytest-cov` |
| `.github/workflows/ci.yml` | Changed — `test` job now produces `coverage.xml`; new `sonarqube` job runs the scan + enforces the Quality Gate |
| `.gitignore` | Changed — ignore generated `coverage.xml` |
| `docs/DAY_7_COMPLETION.md` | New — this file |

## Verification Performed Locally

```bash
pip install -r requirements.txt
pytest tests/ -v --tb=short --cov=app --cov-report=xml --cov-report=term
# -> 2 passed, coverage.xml written, 40% line coverage on app.py
```

The `sonarqube` job itself could not be exercised end-to-end here since it
needs a live SonarQube server + secrets — see "Manual Setup Required" above.

## Acceptance Criteria (Tag07.md, TechStyle-repo scope)

- [x] `sonar-project.properties` present with `sonar.qualitygate.wait=true`
- [x] Quality Gate wiring integrated in CI pipeline (`sonarqube` job)
- [x] Pipeline fails on a red Quality Gate (via `sonar.qualitygate.wait=true`)
- [x] Coverage data (`coverage.xml`) generated and fed to the scanner
- [ ] SonarQube server actually reachable / scan executed at least once —
      requires the manual EC2 provisioning step above (out of this repo's
      scope; infra lives in `musterloesungen-praxisauftraege/tag07/`)
- [ ] Testing-strategy group presentation, SAST Q&A — classroom activities,
      no corresponding TechStyle repo artifact

## Key Learnings

- A Quality Gate only has teeth if it's wired to actually break the build —
  `sonar.qualitygate.wait=true` is what turns "dashboard shows red" into
  "pipeline stops".
- Gating the SonarQube job on secret presence (`if: secrets.X != ''`) is a
  practical way to let a pipeline definition ship ahead of the infrastructure
  it depends on, without breaking CI for everyone in the meantime.
- Coverage is a pipeline artifact like any other: computing it once in
  `test` and passing it to `sonarqube` via `upload-artifact`/`download-artifact`
  avoids running the suite twice.
