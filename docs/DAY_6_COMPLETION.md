# Day 6 Completion — Artifact Management

## What Was Completed

### Task 1: Build Configuration ✅
- Added `pyproject.toml` (PEP 517/518) defining the `techstyle` package.
- The existing `app.py` is packaged as a top-level module (`py-modules = ["app"]`)
  so the file itself, `run_dev.sh`, `deploy.sh`, and the test suite (`from app import app`)
  keep working completely unchanged — packaging was added, nothing was moved.
- Added a `main()` wrapper in `app.py` around the existing `app.run(...)` call and
  registered it as a console-script entry point (`run-techstyle`), so an installed
  artifact can also be started directly.
- Runtime dependency declared explicitly: `Flask>=2.2` (the only third-party import
  `app.py` actually uses).

### Task 2: Automated Artifact Build (Option 1 — `upload-artifact`) ✅
- Extended `.github/workflows/ci.yml` with a `build` job (`needs: test`), so the
  package is only built once linting and tests have passed.
- The job runs `python -m build` (sdist + wheel) and uploads the result with
  `actions/upload-artifact@v4` under the name `techstyle-dist` (14-day retention).
- This gives every push a temporary, downloadable, inspectable build result without
  any external registry.

### Task 3 (Extended — Option 2): Publish to a Self-Hosted PyPI Index ✅
- Added `.github/workflows/publish-pages.yml`, triggered on `v*` tags (or manually).
- Builds sdist + wheel, checks out the `gh-pages` branch, copies the new files into
  `packages/`, regenerates a PEP 503 (`simple/`) index with `dumb-pypi`, and commits
  the updated index back to `gh-pages` using the workflow's built-in `GITHUB_TOKEN`
  (`permissions: contents: write` — no PAT or secret needed).
- **Manual, one-time prerequisites** (not automated by the workflow, and not applied
  by this change since they touch shared repo state):
  1. Create an orphan `gh-pages` branch: `git switch --orphan gh-pages && git commit --allow-empty -m "Initialize PyPI index" && git push origin gh-pages`
  2. Enable GitHub Pages: **Settings → Pages → Source: Deploy from a branch → `gh-pages` / `/(root)`**
  3. Push a version tag once ready: `git tag v1.0.0 && git push origin v1.0.0`
  4. Consume the package elsewhere: `pip install --index-url https://<OWNER>.github.io/<REPO>/simple/ --extra-index-url https://pypi.org/simple techstyle==1.0.0`

### Task 4: README Update ✅
- Added a "Building a Release Artifact" section documenting `python -m build`,
  local install, the `run-techstyle` entry point, and how the CI/CD pipeline
  produces and (optionally) publishes the artifact.

## Files Added / Changed

| File | Change |
|------|--------|
| `pyproject.toml` | New — build configuration for the `techstyle` package |
| `app.py` | Changed — `app.run(...)` moved into a `main()` function used as the console-script entry point; behavior unchanged |
| `.github/workflows/ci.yml` | Changed — added `build` job (depends on `test`) that builds and uploads the artifact |
| `.github/workflows/publish-pages.yml` | New — tag-triggered publish to a PEP 503 index on GitHub Pages |
| `README.md` | Changed — documented the build/artifact workflow |
| `docs/DAY_6_COMPLETION.md` | New — this file |

## Verification Performed Locally

```bash
python -m build                                    # builds dist/techstyle-1.0.0-py3-none-any.whl + .tar.gz
pip install dist/techstyle-1.0.0-py3-none-any.whl   # installs cleanly into a fresh venv
python -c "from app import app; print(len(app.url_map._rules))"  # imports and registers all routes
```

## Known Limitation

The wheel only bundles `app.py` (declared via `py-modules`), not `templates/` or
`static/` — those remain sibling assets, exactly as `deploy.sh` already treats them
(it `scp`s `app.py`, `templates/`, `static/` separately). A `pip install`ed artifact
therefore has all routes and logic, but needs `templates/`/`static/` alongside it to
actually render pages. This mirrors a real constraint of Python packaging (see
Reflexion below) rather than something to silently paper over.

## Reflexion

**Wann reicht ein temporäres Artefakt (Option 1) aus – wann braucht es einen echten Index (Option 2)?**
`upload-artifact` reicht für Debugging, PR-Review-Builds oder einmalige Weitergabe
innerhalb des Teams. Sobald ein anderes Projekt/Environment das Paket per
`pip install <name>==<version>` referenzieren soll (z. B. eine Staging- oder
Test-Umgebung, die den letzten Release konsumiert), braucht es einen echten,
dauerhaften Index — die 90-Tage-Aufbewahrung und die fehlende Versionsauflösung
von `upload-artifact` reichen dafür nicht.

**Vor-/Nachteile temporäre Artefakte vs. Index-Publikation?**
`upload-artifact` ist schnell eingerichtet, kostet nichts an Infrastruktur, ist aber
nur im Actions-UI sichtbar, nicht per `pip install` konsumierbar und läuft nach der
Retention-Zeit ab. Ein Index ist dauerhaft, versioniert und regulär installierbar,
erfordert aber den zusätzlichen `gh-pages`-Aufbau und Disziplin bei der Versionierung.

**Welche Qualitätsanforderungen vor einer Index-Publikation?**
Die `build`-Job-Abhängigkeit von `test` (siehe `ci.yml`) stellt sicher, dass nur
Artefakte gebaut werden, deren Tests bereits grün sind. Vor einer echten Publikation
in den Index sollten zusätzlich Security-/Dependency-Scans (Thema Day 11) und ein
manuelles Tag-Review stehen, da veröffentlichte Versionen laut Konvention
unveränderlich sind.

**Wie werden Versionen konsistent erhöht?**
Über Git-Tags (`vX.Y.Z`), die exakt mit `version` in `pyproject.toml` übereinstimmen
müssen — der Tag ist der einzige Trigger für `publish-pages.yml`. Eine zukünftige
Verbesserung wäre ein automatischer Check, der Tag und `pyproject.toml`-Version im
Workflow vergleicht und bei Abweichung fehlschlägt.

**Kriterium: nur `upload-artifact` oder zusätzlich Index-Publish?**
Faustregel: Wird das Ergebnis nur innerhalb desselben Workflow-Laufs oder für kurzes
manuelles Nachschauen gebraucht → `upload-artifact` reicht. Wird das Paket von einem
anderen Repo, einer anderen Umgebung oder zu einem späteren Zeitpunkt erneut
installiert → Index-Publish.

**Einschränkung des GitHub-Pages-Index bezüglich Vertraulichkeit?**
GitHub Pages ist immer öffentlich zugänglich, auch bei privatem Repository. Der
eigene Index ist also "privat" im Sinne von *selbstverwaltet*, nicht *zugriffs­geschützt*.
Für vertrauliche Pakete (z. B. mit Kundendaten-Logik oder Secrets) müsste stattdessen
ein echter privater Registry-Dienst (Azure Artifacts, JFrog Artifactory, Nexus) genutzt
werden.

## Acceptance Criteria

- [x] Build artifact concept explained (see Reflexion + theory reference in `Tag06.md`)
- [x] GitHub Actions workflow for artifact creation (`ci.yml` `build` job)
- [x] Artifact downloadable/inspectable via Actions UI (`techstyle-dist`)
- [x] Artifact generated from the Flask project (`pyproject.toml` + `python -m build`)
- [x] Artifact repository usage demonstrated (PEP 503 index on GitHub Pages via `publish-pages.yml`)

## Testing Instructions

```bash
# Build and install locally
python -m pip install build
python -m build
pip install dist/techstyle-1.0.0-py3-none-any.whl

# Run existing test suite (unaffected by the packaging change)
pip install -r requirements.txt
pytest tests/ -v --tb=short
flake8 tests/ conftest.py --max-line-length=100 --ignore=E302,W503
```

## Key Learnings

- Packaging does not require restructuring a project — `py-modules` lets an existing
  flat `app.py` become a proper installable artifact with zero disruption to the
  existing dev/deploy scripts.
- Python does not force artifact creation the way Maven/NuGet do; it's a deliberate
  choice, and `pyproject.toml` + `build` is the modern, tool-agnostic way to make it.
- `upload-artifact` and a real package index solve different problems: temporary
  workflow-scoped storage vs. durable, versioned, installable distribution.
- `dumb-pypi` + GitHub Pages gives a fully GitHub-native PEP 503 index without any
  external platform or secret — at the cost of the index being publicly reachable.
