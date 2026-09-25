import os
import shutil
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
import yt_dlp
from config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

# FFmpeg manzilini aniqlash (Windows va Linux/Render uchun)
def get_ffmpeg_path() -> Optional[str]:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

FFMPEG_PATH = get_ffmpeg_path()

# Vaqtni formatlash (masalan, 185 sekund -> 03:05)
def format_duration(seconds: Optional[int]) -> str:
    if not seconds or seconds <= 0:
        return "Noma'lum"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

# Qidiruv keshini saqlash (bir xil qidiruvlar takrorlanganda bir zumda javob berish uchun)
_search_cache: Dict[str, Tuple[float, List[Dict]]] = {}
# Telegram file_id keshi (yuklab olingan musiqalarni qayta yuklamasdan darhol yuborish uchun)
telegram_file_cache: Dict[str, str] = {}

def _search_sync(query: str, limit: int = 10) -> List[Dict]:
    """Tezkor flat-search (faqat metama'lumotlarni tortadi, 1-2 soniyada topadi)."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
    }
    
    search_query = f"ytsearch{limit}:{query}"
    results = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if not info or "entries" not in info:
                return []
            
            for entry in info.get("entries", []):
                if not entry:
                    continue
                video_id = entry.get("id")
                title = entry.get("title", "Noma'lum qo'shiq")
                duration = entry.get("duration")
                uploader = entry.get("uploader") or entry.get("channel", "")
                
                # Agar video bo'lmasa yoki id yo'q bo'lsa o'tkazib yuborish
                if not video_id:
                    continue
                
                results.append({
                    "id": video_id,
                    "title": title,
                    "duration": duration,
                    "duration_str": format_duration(duration),
                    "uploader": uploader,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                })
                if len(results) >= limit:
                    break
    except Exception as e:
        logger.error(f"Qidiruvda xatolik: {e}")
        
    return results

async def search_music(query: str, limit: int = 10) -> List[Dict]:
    """Asinxron qidiruv funksiyasi."""
    query_key = query.strip().lower()
    
    # Keshda bormi tekshirish
    if query_key in _search_cache:
        timestamp, cached_res = _search_cache[query_key]
        return cached_res

    # Asinxron oqimda ishga tushirish (bot qotib qolmasligi uchun)
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(None, _search_sync, query, limit)
    
    if results:
        _search_cache[query_key] = (asyncio.get_event_loop().time(), results)
        
    return results

def _download_sync(video_id: str) -> Optional[Dict]:
    """Musiqani MP3 qilib tez yuklab olish."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "writethumbnail": False,
    }
    
    if FFMPEG_PATH:
        ydl_opts["ffmpeg_location"] = FFMPEG_PATH
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None
            
            title = info.get("title", "Qo'shiq")
            uploader = info.get("uploader") or info.get("channel", "Noma'lum ijrochi")
            duration = info.get("duration", 0)
            
            # Kutilgan fayl yo'li
            expected_mp3 = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
            if os.path.exists(expected_mp3):
                file_path = expected_mp3
            else:
                # Agar ffmpeg bo'lmasa asl yuklangan audio fayl (masalan .m4a, .webm)
                files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.startswith(video_id)]
                if files:
                    file_path = files[0]
                else:
                    return None
            
            return {
                "file_path": file_path,
                "title": title,
                "uploader": uploader,
                "duration": duration,
                "video_id": video_id
            }
    except Exception as e:
        logger.error(f"Yuklab olishda xatolik ({video_id}): {e}")
        return None

async def download_audio(video_id: str) -> Optional[Dict]:
    """Asinxron yuklab olish funksiyasi."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _download_sync, video_id)

def cleanup_file(file_path: Optional[str]):
    """Yuklangan faylni server xotirasidan o'chirish."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Faylni o'chirishda xatolik ({file_path}): {e}")
