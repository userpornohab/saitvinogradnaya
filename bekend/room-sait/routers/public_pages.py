"""Serve Vue's built HTML with public room metadata before JavaScript runs."""
from html import escape
from html.parser import HTMLParser
import os
from urllib.request import urlopen
from xml.etree import ElementTree as ET
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session, selectinload

from database.database import get_db
from models.room import Room, SiteInfo

router = APIRouter(include_in_schema=False)
SITE_URL = os.getenv("PUBLIC_SITE_URL", "https://vinegrape.ru").rstrip("/")
API_URL = os.getenv("PUBLIC_API_URL", "https://api.vinegrape.ru").rstrip("/")
SITE_NAME = "Виноградная Лоза"
LETTERS = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", (
    "a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o",
    "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya")))


def room_path(room):
    title = "".join(LETTERS.get(char, char) for char in room.title.lower())
    slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-")[:80] or "room"
    return f"/rooms/{room.id}-{slug}"


def media_url(value):
    if not value:
        return SITE_URL + "/favicon.png"
    if value.startswith(("https://", "http://")):
        return value
    return API_URL + "/" + value.lstrip("/")


class MetadataHTML(HTMLParser):
    def __init__(self, metadata, fallback):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.metadata = metadata
        self.fallback = fallback
        self.in_head = False
        self.skip_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if self.in_head:
            if tag == "title":
                self.skip_title = True
                return
            if tag == "meta" and (attrs.get("name") in {"description", "robots"}
                                  or attrs.get("property", "").startswith("og:")
                                  or attrs.get("name", "").startswith("twitter:")):
                return
            if tag == "link" and attrs.get("rel") == "canonical":
                return
        self.output.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "title" and self.skip_title:
            self.skip_title = False
            return
        if tag == "head":
            self.output.append(self.metadata)
            self.in_head = False
        if tag == "body":
            self.output.append(self.fallback)
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip_title:
            self.output.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def load_template():
    # A fixed internal URL, never supplied by a visitor. /index.html is static in nginx.
    try:
        with urlopen(os.getenv("FRONTEND_TEMPLATE_URL", "http://frontend/index.html"), timeout=3) as response:
            return response.read(512 * 1024).decode("utf-8")
    except (OSError, UnicodeError):
        raise HTTPException(503, "Frontend template unavailable")


def render_page(title, description, image, path, fallback, status=200):
    values = {"description": description, "robots": "index, follow" if status == 200 else "noindex, nofollow",
              "og:type": "website", "og:title": title, "og:description": description,
              "og:image": image, "og:url": SITE_URL + path, "og:site_name": SITE_NAME,
              "og:locale": "ru_RU", "twitter:card": "summary_large_image", "twitter:title": title,
              "twitter:description": description, "twitter:image": image}
    metadata = f"<title>{escape(title)}</title>"
    for key, value in values.items():
        attribute = "property" if key.startswith("og:") else "name"
        metadata += f'<meta {attribute}="{key}" content="{escape(value, quote=True)}">'
    metadata += f'<link rel="canonical" href="{escape(SITE_URL + path, quote=True)}">'
    parser = MetadataHTML(metadata, f"<noscript>{fallback}</noscript>")
    parser.feed(load_template())
    parser.close()
    return HTMLResponse("".join(parser.output), status_code=status, headers={"Cache-Control": "no-cache"})


@router.get("/public-pages/")
def home_page(db: Session = Depends(get_db)):
    rooms = db.query(Room).order_by(Room.id).all()
    site = db.query(SiteInfo).first()
    description = (site.main_description if site else None) or "Гостевой дом в Рыбачьем, Крым. Номера, двор и отдых у моря."
    links = "".join(f'<li><a href="{room_path(room)}">{escape(room.title)}</a></li>' for room in rooms)
    return render_page(f"{SITE_NAME} - гостевой дом в Крыму", description[:250],
                       media_url(site.main_photo if site else None), "/",
                       f"<h1>{SITE_NAME}</h1><p>{escape(description)}</p><ul>{links}</ul>")


@router.get("/public-pages/rooms/{slug}")
def room_page(slug: str, request: Request, db: Session = Depends(get_db)):
    match = re.match(r"^(\d+)(?:-|$)", slug)
    room = db.query(Room).options(selectinload(Room.photos)).filter(Room.id == int(match[1])).first() if match else None
    if room is None:
        return render_page("Номер не найден", "Номер не найден", media_url(None), "/rooms/" + slug,
                           '<a href="/">На главную</a>', status=404)
    path = room_path(room)
    if "/rooms/" + slug != path:
        query = "?" + request.url.query if request.url.query else ""
        return RedirectResponse(SITE_URL + path + query, status_code=301)
    photos = sorted(room.photos, key=lambda photo: (not photo.is_main, photo.sort_order or 0, photo.id))
    description = " ".join((room.description or room.title).split())
    return render_page(f"{room.title} - {SITE_NAME}", description[:250],
                       media_url(photos[0].url if photos else None), path,
                       f'<h1>{escape(room.title)}</h1><p>{escape(description)}</p><a href="/">Все номера</a>')


@router.get("/public-pages/room={room_id}")
def legacy_room(room_id: int, request: Request, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(404, "Room not found")
    query = "?" + request.url.query if request.url.query else ""
    return RedirectResponse(SITE_URL + room_path(room) + query, status_code=301)


@router.get("/public-pages/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in ["/"] + [room_path(room) for room in db.query(Room).order_by(Room.id).all()]:
        ET.SubElement(ET.SubElement(root, "url"), "loc").text = SITE_URL + path
    return Response(ET.tostring(root, encoding="utf-8", xml_declaration=True), media_type="application/xml")
