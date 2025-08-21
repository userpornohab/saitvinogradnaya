# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from pathlib import Path
import shutil
from datetime import datetime

from database.database import get_db, engine, Base
from models.room import RoomPhoto
from routers import (
    auth,
    rooms,
    bookings,
    amenities,
    bed_options,
    price_periods,
    site  
)

app = FastAPI()


# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
Base.metadata.create_all(bind=engine)

# Создание директорий для файлов
ICON_DIR = Path("static/icons")
ICON_DIR.mkdir(parents=True, exist_ok=True)  # Создаем директорию

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-icon")
async def upload_icon(file: UploadFile = File(...)):
    try:
        if file.content_type not in ["image/svg+xml", "image/png", "image/jpeg"]:
            raise HTTPException(400, "Invalid file type")
        
        filename = f"icon_{datetime.now().strftime('%Y%m%d%H%M%S')}{Path(file.filename).suffix}"
        filepath = ICON_DIR / filename
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"icon_url": f"/static/icons/{filename}"}
    
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


# Каскадное удаление файлов
@event.listens_for(RoomPhoto, 'after_delete')
def delete_photo_file(mapper, connection, target):
    filepath = Path("static/uploads") / target.url.split("/")[-1]
    if filepath.exists():
        try:
            filepath.unlink()
        except Exception as e:
            print(f"Error deleting file: {e}")