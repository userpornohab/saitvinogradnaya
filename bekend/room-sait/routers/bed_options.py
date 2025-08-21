from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from fastapi import UploadFile, File, Form
from database.database import get_db
from schemas.room import BedOptionResponse
from auth.dependencies import check_superuser
from models.room import BedOption, RoomBedOption

router = APIRouter(prefix="/bed-options", tags=["bed-options"])

@router.post("/", response_model=BedOptionResponse, dependencies=[Depends(check_superuser)])
async def create_bed_option(
    name: str = Form(...),
    icon: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Генерация уникального имени файла
    upload_dir = "static/icons"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(icon.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Сохранение файла
    with open(file_path, "wb") as buffer:
        content = await icon.read()
        buffer.write(content)
    
    # Создание записи в БД
    bed_option = BedOption(
        name=name,
        icon=f"static/icons/{filename}"  # Сохраняем путь
    )
    
    db.add(bed_option)
    db.commit()
    db.refresh(bed_option)
    
    return bed_option

@router.get("/", response_model=List[BedOptionResponse])
def get_all_bed_options(db: Session = Depends(get_db)):
    return db.query(BedOption).all()

@router.delete("/{bed_id}", dependencies=[Depends(check_superuser)])
def delete_bed_option(bed_id: int, db: Session = Depends(get_db)):
    """
    Удаление опции кровати вместе со всеми связями
    """
    # Находим опцию кровати
    bed_option = db.query(BedOption).filter(BedOption.id == bed_id).first()
    if not bed_option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bed option not found"
        )

    try:
        # Удаляем все связи с комнатами
        db.query(RoomBedOption).filter(RoomBedOption.bed_option_id == bed_id).delete()
        
        # Удаляем файл иконки (если используется файловая система)
        if bed_option.icon and os.path.exists(bed_option.icon):
            os.remove(bed_option.icon)
        
        # Удаляем саму опцию
        db.delete(bed_option)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting bed option: {str(e)}"
        )

    return {"message": "Bed option deleted successfully"}