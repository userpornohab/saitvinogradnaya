# Deploy

Guest accounts and online payments: see [GUEST_BOOKING_SETUP.md](GUEST_BOOKING_SETUP.md)
before enabling Robokassa. Payments are disabled by default; configure SMTP,
separate test/live credentials, callback URLs and legal/fiscal settings first.

## Server prerequisites

- Ubuntu server with Docker and Docker Compose plugin installed.
- DNS records:
  - `vinegrape.ru` -> server IP
  - `api.vinegrape.ru` -> server IP
- Ports `80` and `443` open.

## First deploy

```bash
git clone <repo-url> vinegrape
cd vinegrape
cp .env.example .env
nano .env
```

Set production values in `.env`:

```env
SECRET_KEY=<long-random-secret>
DATABASE_URL=sqlite:///./data/database.db
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_BOT_USERNAME=<bot_username_without_at>
TELEGRAM_MANAGER_CHAT_ID=<manager_chat_id>
TELEGRAM_API_PROXY=
```

Prepare Traefik certificate storage:

```bash
touch traefik/acme.json
chmod 600 traefik/acme.json
docker compose config --quiet
docker compose up -d --build
```

## Update deploy

Before the first deployment of the hardening update, keep the current volumes.
Never run `docker compose down -v`. Build the backup image and take a verified
snapshot BEFORE restarting the backend (this also works with the previous backend).

```bash
cd vinegrape
git pull
docker compose build backup
docker compose run --rm --no-deps backup
docker compose up -d --build
docker compose ps
```

## Useful checks

```bash
docker compose logs -f backend
docker compose logs -f bot
docker compose logs -f frontend
curl -fsS https://api.vinegrape.ru/health
```

## Backups

SQLite database and uploaded files live in Docker volumes:

- `backend-data` -> `/app/data`
- `backend-static` -> `/app/static`

The `backup` service takes a SQLite online snapshot plus the static files on
startup and then every 24 hours. It verifies the archive and keeps the latest 14
successful archives in `./backups`. Failed snapshots do not replace good backups.
The default source is `/app/data/database.db`; adjust the service's `--database`
argument if you use a different DATABASE_URL. Automatic backups are local to the
server: copy them to another machine/storage for protection against disk failure.

For a consistent database + media snapshot before maintenance, pause writes:

```bash
docker compose stop backend bot backup
docker compose run --rm --no-deps backup
docker compose up -d
```

Daily online backups are transactionally consistent for SQLite. Media can change
during an online backup; use the paused-write procedure above before migrations
or significant media edits. Keep `.env` and Traefik certificates separately and
securely; they are deliberately not included in these archives.

### Verify and rehearse recovery

Replace `ARCHIVE.tar.gz` with a filename from `backups`. These commands only write
to a NEW empty `restore-check` directory, never to running volumes:

```bash
docker compose run --rm --no-deps backup --verify /backups/ARCHIVE.tar.gz
mkdir -p restore-check
docker compose run --rm --no-deps -v "$PWD/restore-check:/restore" backup \
  --restore /backups/ARCHIVE.tar.gz --restore-to /restore
```

For actual recovery, stop backend, bot and backup, preserve a copy of the current
volumes, then copy the restored `data/database.db` and `static/` to their volumes.
Restore to clean data storage so old SQLite WAL/SHM files cannot be reused. Restart
the services and verify rooms, reservations, images and `/health` before reopening
the site. Do not delete the existing volumes as a routine update step.

## Schema migrations

API startup now runs `database.migrate`: it backs up an existing SQLite database
to `data/migration-backups/`, adopts the known schema without replaying old
destructive revisions, and adds availability indexes. A separate Alembic version
table (`deployment_schema_version`) preserves the legacy migration history.
The baseline is frozen in `deployment_migrations/baseline.json`. An unsupported
older schema fails with the table/column names before application writes resume.

For local development, the existing `python -m uvicorn main:app --reload --port 8000`
command still works. To migrate explicitly, run `python -m database.migrate` from
`bekend/room-sait`. Future schema changes must use new revisions in
`deployment_migrations/versions/` and update HEAD in `database/migrate.py`; do not
edit the frozen baseline or run the legacy `alembic upgrade head` on production.

Before applying migrations, rehearse them on a temporary copy of the current DB:
`python -m database.check_upgrade data/database.db` (or `database.db` locally).
This verifies all existing rows and columns are preserved; the source is read-only.
On the server, after building the backend image:
`docker compose run --rm --no-deps --entrypoint python backend -m database.check_upgrade data/database.db`.

## SEO and validation

Nginx sends `/`, `/rooms/...`, legacy `/room=...` and `/sitemap.xml` to public HTML
endpoints on the backend. The backend reads the SAME frontend build at
`http://frontend/index.html` and inserts escaped titles, descriptions, canonical
URLs and Open Graph images. No user-controlled URL is fetched. If the backend is
temporarily unavailable, page routes fall back to the static Vue shell. Local
Vue development continues to use client-side metadata as before.

`/admin/` and `/login` carry `X-Robots-Tag: noindex, nofollow`. robots.txt allows
crawling so bots can see this header; it is not an access-control mechanism.

```bash
curl -fsS https://vinegrape.ru/sitemap.xml
curl -I https://vinegrape.ru/admin/rooms
docker compose logs --tail=50 backend backup
```

Run backend regression tests with `python -m unittest discover -s tests` after
installing `bekend/requirements-dev.txt`. Frontend checks: `npm run lint -- --no-fix`,
`npm run build`, `npx playwright install chromium`, `npm run test:e2e`.
Browser tests use fixtures and never send real Telegram messages or edit live data.
GitHub Actions runs these checks on pushes and pull requests.
