# Deploy

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
docker compose config
docker compose up -d --build
```

## Update deploy

```bash
cd vinegrape
git pull
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

Back them up before risky updates:

```bash
docker run --rm -v vinegrape_backend-data:/data -v "$PWD/backups:/backup" alpine \
  tar czf /backup/backend-data-$(date +%F).tar.gz -C /data .

docker run --rm -v vinegrape_backend-static:/static -v "$PWD/backups:/backup" alpine \
  tar czf /backup/backend-static-$(date +%F).tar.gz -C /static .
```
