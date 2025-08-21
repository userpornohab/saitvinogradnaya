from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from database.database import Base
from .user import User 

class RoomBedOption(Base):
    __tablename__ = "room_bed_options"
    
    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    bed_option_id = Column(Integer, ForeignKey("bed_options.id"), primary_key=True)

class BedOption(Base):
    __tablename__ = "bed_options"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    icon = Column(String(200))  # Путь вида "/static/icons/filename.svg"
    
    rooms = relationship("Room", secondary="room_bed_options", back_populates="bed_options")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in_date = Column(Date)
    check_out_date = Column(Date)
    number_of_guests = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    
    # Новые поля
    guest_name = Column(String(100), nullable=True)
    guest_phone = Column(String(20), nullable=True)
    guest_comment = Column(Text, nullable=True)
    
    room = relationship("Room", back_populates="bookings")
    # Убрали связь с User



# Модель для связи многие-ко-многим (комнаты и удобства)
class RoomAmenity(Base):
    __tablename__ = "room_amenities"
    
    room_id = Column(Integer, ForeignKey("rooms.id"), primary_key=True)
    amenity_id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)

class Amenity(Base):
    __tablename__ = "amenities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    icon = Column(String(100))  # URL иконки
    
    rooms = relationship("Room", secondary="room_amenities", back_populates="amenities")

class PricePeriod(Base):
    __tablename__ = "price_periods"
    
    number_of_guests = Column(Integer, default=1)

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    price = Column(Integer)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    
    room = relationship("Room", back_populates="price_periods")


class RoomPhoto(Base):
    __tablename__ = "room_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(200))
    is_main = Column(Boolean, default=False)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    
    room = relationship("Room", back_populates="photos")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(Text)
    max_guests = Column(Integer)
    number_of_rooms = Column(Integer)
    title_dop = Column(String(100))
    floor = Column(Integer, nullable=True)  # Добавленное поле этажа

    # Relationships
    bed_options = relationship("BedOption", secondary="room_bed_options", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room", cascade="all, delete" )
    photos = relationship("RoomPhoto", back_populates="room", cascade="all, delete")
    price_periods = relationship("PricePeriod", back_populates="room", cascade="all, delete")
    amenities = relationship("Amenity", secondary="room_amenities", back_populates="rooms")


class SiteInfo(Base):
    __tablename__ = "site_info"
    
    id = Column(Integer, primary_key=True, index=True, default=1)
    main_photo = Column(String(200), nullable=True)
    main_description = Column(Text, nullable=True)

class CourtyardPhoto(Base):
    __tablename__ = "courtyard_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(200))
    site_info_id = Column(Integer, ForeignKey("site_info.id"), default=1)
    
    site_info = relationship("SiteInfo", backref="courtyard_photos")

class Testimonial(Base):
    __tablename__ = "testimonials"
    
    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String(100))
    author_icon_url = Column(String(200))
    comment = Column(Text)
    site_info_id = Column(Integer, ForeignKey("site_info.id"), default=1)
    
    site_info = relationship("SiteInfo", backref="testimonials")

class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    site_info_id = Column(Integer, ForeignKey("site_info.id"), default=1)
    
    site_info = relationship("SiteInfo", backref="faqs")