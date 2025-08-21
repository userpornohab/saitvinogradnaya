from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from models.room import RoomAmenity, Amenity
from schemas.room import AmenityBase
from auth.dependencies import check_superuser
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
router = APIRouter(prefix="/amenities", tags=["amenities"])




@router.delete("/{amenity_id}", dependencies=[Depends(check_superuser)])
def delete_amenity(amenity_id: int, db: Session = Depends(get_db)):
    amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
    if not amenity:
        raise HTTPException(status_code=404, detail="Удобство не найдено")
    
    # Удаление связей с комнатами
    db.query(RoomAmenity).filter(RoomAmenity.amenity_id == amenity_id).delete()
    
    # Удаление файла иконки
    if amenity.icon:
        try:
            os.remove(amenity.icon)
        except Exception as e:

            print(amenity.icon)
            pass  # Логируйте ошибку при необходимости
    
    # Удаление самого удобства
    db.delete(amenity)
    db.commit()
    
    return {"message": "Удобство удалено"}

@router.post("/", response_model=AmenityBase, dependencies=[Depends(check_superuser)])
async def create_amenity(
    name: str = Form(...),
    icon: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Генерация уникального имени файла
    file_ext = os.path.splitext(icon.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("static/icons", filename)
    
    # Создание директории
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Сохранение файла
    with open(file_path, "wb") as buffer:
        content = await icon.read()
        buffer.write(content)
    
    # Создание записи
    amenity = Amenity(name=name, icon=file_path)
    db.add(amenity)
    db.commit()
    db.refresh(amenity)
    
    return amenity

@router.get("/", response_model=List[AmenityBase])
def get_all_amenities(db: Session = Depends(get_db)):
    """Получение всех удобств"""
    return db.query(Amenity).all()
