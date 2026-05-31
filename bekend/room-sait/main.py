# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import event
from sqlalchemy import inspect, text
from pathlib import Path

from database.database import get_db, engine, Base
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
    calendar_sync
)

app = FastAPI()


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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
Base.metadata.create_all(bind=engine)

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

# Создание директорий для файлов
ICON_DIR = Path("static/icons")
ICON_DIR.mkdir(parents=True, exist_ok=True)  # Создаем директорию

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def ensure_courtyard_photo_columns():
    inspector = inspect(engine)
    if "courtyard_photos" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("courtyard_photos")}
    with engine.begin() as connection:
        if "category" not in columns:
            connection.execute(text("ALTER TABLE courtyard_photos ADD COLUMN category VARCHAR(30) DEFAULT 'yard'"))
        if "sort_order" not in columns:
            connection.execute(text("ALTER TABLE courtyard_photos ADD COLUMN sort_order INTEGER DEFAULT 0"))

ensure_courtyard_photo_columns()

def ensure_room_photo_columns():
    inspector = inspect(engine)
    if "room_photos" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("room_photos")}
    with engine.begin() as connection:
        if "sort_order" not in columns:
            connection.execute(text("ALTER TABLE room_photos ADD COLUMN sort_order INTEGER DEFAULT 0"))

ensure_room_photo_columns()

def ensure_room_calendar_columns():
    inspector = inspect(engine)
    if "rooms" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("rooms")}
    with engine.begin() as connection:
        if "calendar_token" not in columns:
            connection.execute(text("ALTER TABLE rooms ADD COLUMN calendar_token VARCHAR(64)"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_rooms_calendar_token ON rooms(calendar_token)"))

ensure_room_calendar_columns()

@app.post("/upload-icon")
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


# Каскадное удаление файлов
@event.listens_for(RoomPhoto, 'after_delete')
def delete_photo_file(mapper, connection, target):
    filepath = Path("static/uploads") / target.url.split("/")[-1]
    if filepath.exists():
        try:
            filepath.unlink()
        except Exception as e:
            print(f"Error deleting file: {e}")
