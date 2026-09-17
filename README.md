# Praxis

## Aufsetzen von SonarQube Community Server auf EC2 VM mit Docker Compose

#### Sozialform

Gruppenarbeit in 2er Teams:
- Person 1: DevOps/Platform-Engineer kümmert sich um VM-Setup und Docker Deployment
- Person 2: Applikationsentwickler mit Python Repo für SonarQube-Scan Integration

#### Ziel:
SonarQube Community Edition auf einer EC2 VM mit Elastic IP mittels Docker Compose deployen. Automatisierung via Terraform und Cloud-Init.

#### Voraussetzung
- AWS CLI konfiguriert mit Learner Lab Credentials
- Terraform installiert
- Ein GitHub Repo mit Python-Code für SonarQube-Scans

#### Musterlösung nutzen

Die komplette Musterlösung für diesen Auftrag ist im externen Repository auf dem `day_7_solution` Branch verfügbar:
📁 **[tbzdevops/musterloesungen-praxisauftraege/day_7_solution](https://github.com/tbzdevops/musterloesungen-praxisauftraege/tree/day_7_solution)**

**Dateien in der Musterlösung:**

- `sonarqube-vm.tf` — Terraform Manifest für EC2 VM mit 30 GB Diskspace, Security Group, Elastic IP
- `cloud-init.yml` — Cloud-Init Script mit Docker Setup und systemd Service für SonarQube
- `docker-compose.yml` — Docker Compose Konfiguration mit PostgreSQL und SonarQube Community
- `README.md` — Zusätzliche Dokumentation

#### Schritte:

**1. Musterlösung klonen oder kopieren** (Person 1)

   ```bash
   # Option 1: Musterlösungs-Repo klonen (day_7_solution Branch)
   git clone -b day_7_solution https://github.com/tbzdevops/musterloesungen-praxisauftraege.git
   cd musterloesungen-praxisauftraege/

   # Option 2: Oder nur mit Shallow Clone für schnelleres Klonen
   git clone -b day_7_solution --depth 1 https://github.com/tbzdevops/musterloesungen-praxisauftraege.git tag07-solution
   cd tag07-solution/
   ```

**2. Terraform initialisieren und VM erstellen** (Person 1)

   ```bash
   # Terraform initialisieren
   terraform init

   # Plan anschauen
   terraform plan

   # VM erstellen (dauert ~5 Minuten)
   terraform apply

   # Elastic IP wird angezeigt
   # Beispielausgabe:
   # sonarqube_ip = "54.123.45.67"
   # sonarqube_url = "http://54.123.45.67:9000"
   # startup_notice = "SonarQube needs about 5 minutes to start up..."
   ```

   **Terraform-Features der Musterlösung:**

   - ✅ Ubuntu 26.04 LTS AMI (aktuellste Sicherheitsupdates)
   - ✅ t3.large Instance (8GB RAM, ausreichend für SonarQube)
   - ✅ 30 GB EBS Volume (gp3) für Docker & Datenbanken
   - ✅ Security Group mit SSH (Port 22) und SonarQube (Port 9000)
   - ✅ Elastic IP für stabile externe Erreichbarkeit
   - ✅ Cloud-Init Integration für automatisches Setup
   - ✅ SSH Key Injection (falls ~/.ssh/id_rsa.pub vorhanden)

**3. Cloud-Init Features verstehen** (Person 1)

   Die Musterlösung nutzt ein optimiertes Cloud-Init Script mit:

   **Systemd Service für SonarQube:**
   
   ```bash
   /etc/systemd/system/sonarqube.service
   ```

   - Automatischer Start beim Reboot
   - `docker compose up -d` als Service managed
   - `docker compose down` bei Shutdown
   - Automatische Neustarts bei Fehlern

   **Docker Compose Setup:**
   
   - PostgreSQL 17 für Persistierung
   - SonarQube Community Edition
   - Named Volumes für Datenpersistierung
   - Health Checks für Service-Readiness
   - Bridge Network für Kommunikation

**4. Warte auf SonarQube Start** (Person 1)

   ```bash
   # SSH in die VM
   SONARQUBE_IP=$(terraform output -raw sonarqube_ip)
   ssh -i ~/.ssh/id_rsa ubuntu@$SONARQUBE_IP

   # In der VM: Logs prüfen
   cd /opt/sonarqube
   docker compose logs -f sonarqube

   # Warte bis: "SonarQube is up" erscheint (ca. 5 Minuten)
   # Dann: Ctrl+C zum Beenden
   exit
   ```

   ⏳ **Hinweis:** Das Terraform Output gibt auch einen `startup_notice` aus.

**5. Zugriff auf SonarQube im Browser** (Person 1)

   ```bash
   # Hole Elastic IP
   SONARQUBE_IP=$(terraform output -raw sonarqube_ip)
   echo "Öffne: http://$SONARQUBE_IP:9000"
   ```

   - Öffne im Browser: `http://<ELASTIC-IP>:9000`
   - Standard-Login: Benutzer `admin`, Passwort `admin`

**6. SonarQube initial konfigurieren** (Person 1)
   
   - Passwort ändern
   - Neuen User für **Person 2** erstellen
   - Logins/Tokens an Person 2 weitergeben
   - Lokales Projekt erstellen ("Create a local project")

**7. Projekt in SonarQube erstellen** (Person 2)
   
   - Mit neuem User in SonarQube anmelden
   - "Create a local project" wählen
   - Projekt-Name `techstyle` eingeben
   - Branch wählen: `main` oder `master`
   - "Use the global settings" wählen
   - Analysis Method: `GitHub Action` für automatisierte Scans -> Instruktionen für Python und Tokens speichern für setup in Projekt und Schritt 8

**8. Testmässig Einbauen in Repo**

  - Benutze die Instruktionen aus Schritt 7 um einen zusätzlichen Schritt in die Pipeline zu bauen.

<br>