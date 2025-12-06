# ⟶̽ जय श्री ༢།म > 𝟑🙏🚩
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

# Constants
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Thumbnail layout (NEW HALF-SPLIT DESIGN)
CANVAS_W, CANVAS_H = 1280, 720
LEFT_W = CANVAS_W // 2       # 640px
RIGHT_W = CANVAS_W // 2      # 640px

RIGHT_X = LEFT_W             # thumbnail starts at middle
RIGHT_Y = 0

LEFT_X = 0
LEFT_Y = 0

# Soft outer shadow (S1)
SHADOW_BLUR = 20  # subtle, premium

# Font safe load
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

title_font = load_font("RiteshMusic/assets/thumb/font2.ttf", 40)
meta_font = load_font("RiteshMusic/assets/thumb/font.ttf", 22)
duration_font = load_font("RiteshMusic/assets/thumb/font2.ttf", 30)

def clean_text(t):
    return re.sub(r"\s+", " ", t).strip()

async def get_thumb(videoid: str) -> str:
    out_path = os.path.join(CACHE_DIR, f"{videoid}_v5.png")
    if os.path.exists(out_path):
        return out_path

    # fetch info
    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        data = await results.next()
        info = data["result"][0]

        title = clean_text(info.get("title", "Unknown Title"))
        thumb = info.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = info.get("duration")
        views = info.get("viewCount", {}).get("short", "Unknown Views")

    except:
        title = "Unknown Title"
        thumb = YOUTUBE_IMG_URL
        duration = None
        views = "Unknown Views"

    is_live = not duration or str(duration).lower() in ["", "live", "live now"]
    duration_text = "LIVE" if is_live else duration or "Unknown"

    # download thumbnail
    temp_thumb = os.path.join(CACHE_DIR, f"temp_{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumb) as resp:
                if resp.status == 200:
                    async with aiofiles.open(temp_thumb, "wb") as f:
                        await f.write(await resp.read())
    except:
        return YOUTUBE_IMG_URL

    # final canvas
    base = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))

    # right half thumbnail
    right_img = Image.open(temp_thumb).convert("RGBA")
    right_img = right_img.resize((RIGHT_W, CANVAS_H))

    # paste right side
    base.paste(right_img, (RIGHT_X, RIGHT_Y))

    # left panel
    draw = ImageDraw.Draw(base)

    padding = 40
    text_x = LEFT_X + padding
    text_y = LEFT_Y + padding

    # Title
    draw.text((text_x, text_y), title, font=title_font, fill="white")
    text_y += 60

    # Views
    draw.text((text_x, text_y), f"Views: {views}", font=meta_font, fill="#e0e0e0")
    text_y += 40

    # Duration badge (premium aesthetic)
    dur_w, dur_h = draw.textsize(duration_text, font=duration_font)
    badge_pad = 20
    bx1 = text_x
    by1 = text_y
    bx2 = bx1 + dur_w + badge_pad
    by2 = by1 + dur_h + 10

    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=12, fill=(255, 255, 255, 25))
    draw.text((bx1 + 10, by1 + 5), duration_text, font=duration_font, fill="white")

    # Outer soft shadow (S1)
    shadow = base.copy().convert("RGBA")
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))

    final = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    final.alpha_composite(shadow, (0, 0))
    final.alpha_composite(base, (0, 0))

    final.save(out_path)

    try:
        os.remove(temp_thumb)
    except:
        pass

    return out_path
