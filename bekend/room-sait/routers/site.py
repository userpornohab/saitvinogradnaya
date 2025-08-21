from typing import Optional,List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database.database import get_db
from models.room import SiteInfo, CourtyardPhoto, Testimonial, FAQ
from schemas.room import (
    SiteInfoResponse,
    CourtyardPhotoResponse,
    TestimonialResponse,
    FAQCreate,
    SiteInfoBase,
    FAQResponse
)
from auth.dependencies import check_superuser
from pathlib import Path
import shutil
import os
from datetime import datetime

router = APIRouter(prefix="/site", tags=["site"])

def get_or_create_site_info(db: Session):
    site_info = db.query(SiteInfo).filter(SiteInfo.id == 1).first()
    if not site_info:
        site_info = SiteInfo()
        db.add(site_info)
        db.commit()
        db.refresh(site_info)
    return site_info

@router.get("/", response_model=SiteInfoResponse)
def get_site_info(db: Session = Depends(get_db)):
    site_info = get_or_create_site_info(db)
    return site_info

@router.put("/", response_model=SiteInfoBase, dependencies=[Depends(check_superuser)])
async def update_site_info(
    main_description: Optional[str] = Form(None),
    main_photo_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    site_info = get_or_create_site_info(db)
    
    if main_description is not None:
        site_info.main_description = main_description
        
    if main_photo_file:
        # Удаляем старое фото если существует
        if site_info.main_photo:
            old_path = Path("static") / site_info.main_photo.split("/")[-1]
            if old_path.exists():
                old_path.unlink()
        
        # Сохраняем новое фото
        upload_dir = Path("static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"main_photo_{timestamp}_{main_photo_file.filename}"
        filepath = upload_dir / filename
        
        with filepath.open("wb") as buffer:
            content = await main_photo_file.read()
            buffer.write(content)
        
        site_info.main_photo = f"/static/uploads/{filename}"
    
    db.commit()
    db.refresh(site_info)
    return site_info

@router.post("/courtyard-photos", response_model=List[CourtyardPhotoResponse], dependencies=[Depends(check_superuser)])
async def add_courtyard_photos(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    site_info = get_or_create_site_info(db)
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    saved_photos = []
    saved_files = []
    errors = []

    try:
        for file in files:
            try:
                # Генерируем уникальное имя файла
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
                filename = f"courtyard_{timestamp}_{file.filename}"
                filepath = upload_dir / filename

                # Сохраняем файл
                with filepath.open("wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                saved_files.append(filepath)

                # Создаем запись в БД
                photo = CourtyardPhoto(
                    url=f"/static/uploads/{filename}", 
                    site_info_id=site_info.id
                )
                db.add(photo)
                saved_photos.append(photo)
                
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                # Продолжаем обработку остальных файлов при ошибке

        db.commit()
        
        # Обновляем объекты для возврата
        for photo in saved_photos:
            db.refresh(photo)
        
        if errors:
            # Возвращаем успешные загрузки + ошибки
            return {
                "success": [p.id for p in saved_photos],
                "errors": errors
            }
        
        return saved_photos
        
    except Exception as e:
        # Откатываем транзакцию БД
        db.rollback()
        
        # Удаляем сохраненные файлы при ошибке
        for filepath in saved_files:
            if filepath.exists():
                filepath.unlink()
                
        raise HTTPException(500, f"File upload failed: {str(e)}")
    
    finally:
        # Гарантируем закрытие всех файлов
        for file in files:
            await file.close()

@router.delete("/courtyard-photos/{photo_id}", dependencies=[Depends(check_superuser)])
def delete_courtyard_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    photo = db.query(CourtyardPhoto).filter(CourtyardPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")
    
    # Удаление файла
    if photo.url:
        file_path = os.path.join("static/uploads", os.path.basename(photo.url))
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted"}

@router.post("/testimonials", response_model=TestimonialResponse, dependencies=[Depends(check_superuser)])
async def add_testimonial(
    author_name: str = Form(...),
    comment: str = Form(...),
    author_icon_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    site_info = get_or_create_site_info(db)
    
    # Сохраняем иконку
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"testimonial_icon_{timestamp}_{author_icon_file.filename}"
    filepath = upload_dir / filename
    
    with filepath.open("wb") as buffer:
        content = await author_icon_file.read()
        buffer.write(content)
    
    testimonial = Testimonial(
        author_name=author_name,
        comment=comment,
        author_icon_url=f"/static/uploads/{filename}",
        site_info_id=site_info.id
    )
    
    db.add(testimonial)
    db.commit()
    db.refresh(testimonial)
    return testimonial

# Обновление отзыва
@router.put("/testimonials/{testimonial_id}", response_model=TestimonialResponse, dependencies=[Depends(check_superuser)])
async def update_testimonial(
    testimonial_id: int,
    author_name: Optional[str] = Form(None),
    comment: Optional[str] = Form(None),
    author_icon_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not testimonial:
        raise HTTPException(404, "Testimonial not found")
    
    if author_name is not None:
        testimonial.author_name = author_name
    if comment is not None:
        testimonial.comment = comment
    
    if author_icon_file:
        # Удаляем старую иконку
        if testimonial.author_icon_url:
            old_path = Path("static") / testimonial.author_icon_url.split("/")[-1]
            if old_path.exists():
                old_path.unlink()
        
        # Сохраняем новую иконку
        upload_dir = Path("static/uploads")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"testimonial_icon_{timestamp}_{author_icon_file.filename}"
        filepath = upload_dir / filename
        
        with filepath.open("wb") as buffer:
            content = await author_icon_file.read()
            buffer.write(content)
        
        testimonial.author_icon_url = f"/static/uploads/{filename}"
    
    db.commit()
    db.refresh(testimonial)
    return testimonial

@router.delete("/testimonials/{testimonial_id}", dependencies=[Depends(check_superuser)])
def delete_testimonial(
    testimonial_id: int,
    db: Session = Depends(get_db)
):
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not testimonial:
        raise HTTPException(404, "Testimonial not found")
    
    db.delete(testimonial)
    db.commit()
    return {"message": "Testimonial deleted"}

@router.post("/faqs", response_model=FAQResponse, dependencies=[Depends(check_superuser)])
def add_faq(
    faq_data: FAQCreate,
    db: Session = Depends(get_db)
):
    site_info = get_or_create_site_info(db)
    faq = FAQ(**faq_data.dict(), site_info_id=site_info.id)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq

@router.put("/faqs/{faq_id}", response_model=FAQResponse, dependencies=[Depends(check_superuser)])
def update_faq(
    faq_id: int,
    update_data: FAQCreate,
    db: Session = Depends(get_db)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, "FAQ not found")
    
    for key, value in update_data.dict().items():
        setattr(faq, key, value)
    
    db.commit()
    db.refresh(faq)
    return faq

@router.delete("/faqs/{faq_id}", dependencies=[Depends(check_superuser)])
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db)
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, "FAQ not found")
    
    db.delete(faq)
    db.commit()
    return {"message": "FAQ deleted"}