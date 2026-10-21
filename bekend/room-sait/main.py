# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from auth.dependencies import check_superuser
from contextlib import asynccontextmanager
from database.migrate import upgrade_database
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import event
from pathlib import Path
from config import settings

from models.room import RoomPhoto
from utils.image_upload import save_raw_upload
from routers import (
    auth,
    rooms,
    bookings,
    amenities,
    bed_options,
    price_periods,
    site,
    analytics,
    calendar_sync,
    public_pages,
    guest_auth,
    guest_bookings
)

@asynccontextmanager
async def lifespan(app):
    upgrade_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def response_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.headers.get("authorization") or request.url.path == "/token/" or request.url.path.startswith(("/guest", "/payments/")):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path.startswith("/static/"):
        response.headers["Content-Security-Policy"] = "sandbox; default-src 'none'; style-src 'unsafe-inline'"
    return response


# Middleware для корректной схемы за Traefik (чтобы редиректы были https://)
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        proto = request.headers.get("x-forwarded-proto", "http")
        if proto == "https":
            request.scope["scheme"] = "https"
        host = request.headers.get("x-forwarded-host")
        if host:
            request.scope["server"] = (host, 443 if proto == "https" else 80)
        response = await call_next(request)
        return response

app.add_middleware(ProxyHeadersMiddleware)

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://10.7.0.5:8080",
        "https://vinegrape.ru",
        "http://vinegrape.ru",
    ] + [origin.strip() for origin in settings.GUEST_ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

# Создание директорий для файлов
ICON_DIR = Path("static/icons")
ICON_DIR.mkdir(parents=True, exist_ok=True)  # Создаем директорию

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-icon", dependencies=[Depends(check_superuser)])
async def upload_icon(file: UploadFile = File(...)):
    try:
        icon_url = await save_raw_upload(
            file=file,
            upload_dir=ICON_DIR,
            prefix="icon",
            allowed_types={"image/svg+xml", "image/png", "image/jpeg", "image/webp"},
            max_bytes=1024 * 1024
        )
        return {"icon_url": icon_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"File upload failed: {str(e)}")

# Подключение роутеров
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(amenities.router)
app.include_router(bed_options.router)
app.include_router(price_periods.router)
app.include_router(site.router)
app.include_router(analytics.router)
app.include_router(calendar_sync.router)
app.include_router(public_pages.router)
app.include_router(guest_auth.router)
app.include_router(guest_bookings.router)


# Каскадное удаление файлов
@event.listens_for(RoomPhoto, 'after_delete')
def delete_photo_file(mapper, connection, target):
    filepath = Path("static/uploads") / target.url.split("/")[-1]
    if filepath.exists():
        try:
            filepath.unlink()
        except Exception as e:
            print(f"Error deleting file: {e}")
