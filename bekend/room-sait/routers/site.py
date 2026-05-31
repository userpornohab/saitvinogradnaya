from typing import Optional,List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.database import get_db
from models.room import SiteInfo, CourtyardPhoto, Testimonial, TestimonialImage, FAQ
from schemas.room import (
    SiteInfoResponse,
    CourtyardPhotoResponse,
    TestimonialResponse,
    TestimonialImageResponse,
    FAQCreate,
    SiteInfoBase,
    FAQResponse,
    FAQBase,
    CourtyardPhotoOrderItem,
    CourtyardPhotoUpdate
)
from auth.dependencies import check_superuser
from pathlib import Path
import os
from utils.image_upload import save_upload_image, save_upload_image_or_svg

router = APIRouter(prefix="/site", tags=["site"])

TERRITORY_CATEGORIES = {"yard", "kitchen", "rest"}

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
    site_info.courtyard_photos.sort(key=lambda photo: (photo.category or "yard", photo.sort_order or 0, photo.id))
    site_info.testimonial_images.sort(key=lambda image: (image.sort_order or 0, image.id))
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
            old_path = Path("static/uploads") / os.path.basename(site_info.main_photo)
            if old_path.exists():
                old_path.unlink()
        
        site_info.main_photo = await save_upload_image(
            file=main_photo_file,
            upload_dir=Path("static/uploads"),
            prefix="main_photo"
        )
    
    db.commit()
    db.refresh(site_info)
    return site_info

@router.post("/courtyard-photos", response_model=List[CourtyardPhotoResponse], dependencies=[Depends(check_superuser)])
async def add_courtyard_photos(
    files: List[UploadFile] = File(...),
    category: str = Form("yard"),
    db: Session = Depends(get_db)
):
    if category not in TERRITORY_CATEGORIES:
        raise HTTPException(422, "Unknown territory category")

    site_info = get_or_create_site_info(db)
    upload_dir = Path("static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    saved_photos = []
    saved_files = []
    errors = []

    try:
        max_order = db.query(func.max(CourtyardPhoto.sort_order)).filter(
            CourtyardPhoto.category == category
        ).scalar() or 0

        for index, file in enumerate(files, start=1):
            try:
                photo_url = await save_upload_image(
                    file=file,
                    upload_dir=upload_dir,
                    prefix="courtyard"
                )
                saved_files.append(Path("static/uploads") / os.path.basename(photo_url))

                # Создаем запись в БД
                photo = CourtyardPhoto(
                    url=photo_url,
                    category=category,
                    sort_order=max_order + index,
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

@router.patch("/courtyard-photos/order", response_model=List[CourtyardPhotoResponse], dependencies=[Depends(check_superuser)])
def reorder_courtyard_photos(
    items: List[CourtyardPhotoOrderItem] = Body(...),
    db: Session = Depends(get_db)
):
    updated = []
    for item in items:
        photo = db.query(CourtyardPhoto).filter(CourtyardPhoto.id == item.id).first()
        if not photo:
            continue
        if item.category is not None:
            if item.category not in TERRITORY_CATEGORIES:
                raise HTTPException(422, "Unknown territory category")
            photo.category = item.category
        photo.sort_order = item.sort_order
        updated.append(photo)

    db.commit()
    for photo in updated:
        db.refresh(photo)
    return sorted(updated, key=lambda photo: (photo.category or "yard", photo.sort_order or 0, photo.id))

@router.patch("/courtyard-photos/{photo_id}", response_model=CourtyardPhotoResponse, dependencies=[Depends(check_superuser)])
def update_courtyard_photo(
    photo_id: int,
    update_data: CourtyardPhotoUpdate,
    db: Session = Depends(get_db)
):
    photo = db.query(CourtyardPhoto).filter(CourtyardPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")

    if update_data.category is not None:
        if update_data.category not in TERRITORY_CATEGORIES:
            raise HTTPException(422, "Unknown territory category")
        photo.category = update_data.category

    if update_data.sort_order is not None:
        photo.sort_order = update_data.sort_order

    db.commit()
    db.refresh(photo)
    return photo

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

@router.get("/testimonial-images", response_model=List[TestimonialImageResponse], dependencies=[Depends(check_superuser)])
def get_testimonial_images(db: Session = Depends(get_db)):
    return db.query(TestimonialImage).order_by(TestimonialImage.sort_order, TestimonialImage.id).all()

@router.post("/testimonial-images", response_model=List[TestimonialImageResponse], dependencies=[Depends(check_superuser)])
async def add_testimonial_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    site_info = get_or_create_site_info(db)
    upload_dir = Path("static/uploads")
    saved_images = []
    saved_files = []

    try:
        max_order = db.query(func.max(TestimonialImage.sort_order)).scalar() or 0
        for index, file in enumerate(files, start=1):
            image_url = await save_upload_image_or_svg(
                file=file,
                upload_dir=upload_dir,
                prefix="testimonial_icon"
            )
            saved_files.append(Path("static/uploads") / os.path.basename(image_url))
            image = TestimonialImage(
                url=image_url,
                sort_order=max_order + index,
                site_info_id=site_info.id
            )
            db.add(image)
            saved_images.append(image)

        db.commit()
        for image in saved_images:
            db.refresh(image)
        return saved_images
    except Exception as e:
        db.rollback()
        for filepath in saved_files:
            if filepath.exists():
                filepath.unlink()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(500, f"File upload failed: {str(e)}")
    finally:
        for file in files:
            await file.close()

@router.delete("/testimonial-images/{image_id}", dependencies=[Depends(check_superuser)])
def delete_testimonial_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    image = db.query(TestimonialImage).filter(TestimonialImage.id == image_id).first()
    if not image:
        raise HTTPException(404, "Image not found")

    used_count = db.query(Testimonial).filter(Testimonial.author_icon_url == image.url).count()
    if used_count:
        raise HTTPException(409, "Это фото используется в отзыве")

    if image.url:
        file_path = Path("static/uploads") / os.path.basename(image.url)
        if file_path.exists():
            file_path.unlink()

    db.delete(image)
    db.commit()
    return {"message": "Image deleted"}

@router.post("/testimonials", response_model=TestimonialResponse, dependencies=[Depends(check_superuser)])
async def add_testimonial(
    author_name: str = Form(...),
    comment: str = Form(...),
    author_icon_file: Optional[UploadFile] = File(None),
    author_icon_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    site_info = get_or_create_site_info(db)
    icon_url = author_icon_url

    if author_icon_file:
        icon_url = await save_upload_image_or_svg(
            file=author_icon_file,
            upload_dir=Path("static/uploads"),
            prefix="testimonial_icon"
        )
    
    testimonial = Testimonial(
        author_name=author_name,
        comment=comment,
        author_icon_url=icon_url,
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
    author_icon_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    if not testimonial:
        raise HTTPException(404, "Testimonial not found")
    
    if author_name is not None:
        testimonial.author_name = author_name
    if comment is not None:
        testimonial.comment = comment
    if author_icon_url is not None:
        testimonial.author_icon_url = author_icon_url
    
    if author_icon_file:
        testimonial.author_icon_url = await save_upload_image_or_svg(
            file=author_icon_file,
            upload_dir=Path("static/uploads"),
            prefix="testimonial_icon"
        )
    
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


@router.get("/faqs", response_model=List[FAQResponse])
def get_faq_info(db: Session = Depends(get_db)):
    faq = db.query(FAQ).all()
    return faq

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
