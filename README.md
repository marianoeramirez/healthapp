# Health Tracker

Personal/family Django app for tracking people, health events, doctors, exams/reports, and attachments.

Web UI: `/people/`, `/events/`, `/doctors/`, `/exams/` (login required). Admin: `/admin/`.

Production URL: **https://health.marianoeramirez.com**

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in.

## Deployment (GCP VM + host nginx)

Same machine pattern as Memoria del Alma on this GCE VM:

- Docker runs **only the Django app** on host port **8001**
- **Host nginx** (already on 80/443) reverse-proxies `health.marianoeramirez.com`
- **Host Certbot** issues TLS certificates

```text
push to main → CI → build/push ghcr.io/<owner>/healthapp → SSH → compose up → migrate
```

Do **not** bind Docker nginx to 80/443 on this VM — those ports belong to the system nginx used by `app.memoriadelalma.com`.

### One-time setup on the GCE VM

SSH user: `marianoramirez353` · example host: `34.171.174.54`

1. DNS **A** record: `health.marianoeramirez.com` → VM public IP.
2. Create the deploy directory and files:

   ```bash
   mkdir -p ~/healthapp/data/media ~/healthapp/data/staticfiles ~/healthapp/deploy
   cd ~/healthapp
   # Copy docker-compose.yml, env.example → .env, deploy/nginx-host*.conf from the repo
   cp env.example .env
   # Edit .env: set SECRET_KEY and HEALTHAPP_IMAGE=ghcr.io/marianoeramirez/healthapp:latest
   ```

3. Ensure GHCR login (if the image is private):

   ```bash
   echo "$GHCR_TOKEN" | docker login ghcr.io -u marianoeramirez --password-stdin
   ```

4. Start the app:

   ```bash
   cd ~/healthapp
   docker compose pull
   docker compose up -d
   docker compose exec healthapp python manage.py createsuperuser
   ```

5. Install the host nginx site (HTTP bootstrap first):

   ```bash
   sudo mkdir -p /var/www/certbot
   sudo cp ~/healthapp/deploy/nginx-host.bootstrap.conf /etc/nginx/sites-available/healthapp.conf
   sudo ln -sf /etc/nginx/sites-available/healthapp.conf /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

6. Issue the certificate and enable HTTPS:

   ```bash
   sudo certbot --nginx -d health.marianoeramirez.com
   ```

   Certbot will update the site file with SSL. Confirm static/media aliases still point at:

   `/home/marianoramirez353/healthapp/data/staticfiles/` and `.../media/`

7. Reload nginx if you hand-edited anything:

   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

### GitHub secrets

| Secret | Example / purpose |
|--------|-------------------|
| `DEPLOY_SSH_HOST` | `34.171.174.54` |
| `DEPLOY_SSH_USER` | `marianoramirez353` |
| `DEPLOY_SSH_KEY` | Private key for that user |
| `DEPLOY_PATH` | `/home/marianoramirez353/healthapp` |

### Ongoing deploys

Push to `main`. Deploy workflow runs:

```bash
cd $DEPLOY_PATH
docker compose pull
docker compose up -d
docker compose exec -T healthapp python manage.py migrate --noinput
docker image prune -f
```

### Useful commands

```bash
docker compose -f ~/healthapp/docker-compose.yml logs -f healthapp
curl -I http://127.0.0.1:8001/
sudo nginx -t && sudo systemctl reload nginx
```

SQLite + uploads live under `~/healthapp/data/`. Back that directory up regularly.

## Usage

1. Add **People** (optional avatar, blood type, notes).
2. Add **Health events** (milestones / episodes, with severity).
3. Add **Doctors** (specialty, phone, city, country).
4. Add **Exams** linked to a person, optional event and doctor; upload PDFs/images.
