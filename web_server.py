import logging
from aiohttp import web
from config import PORT

logger = logging.getLogger(__name__)

async def handle_ping(request):
    """Render uchun Health Check / Ping endpoint."""
    return web.json_response({
        "status": "online",
        "service": "Telegram Music Bot",
        "username": "@musiqazuxibot",
        "message": "Bot muvaffaqiyatli ishlamoqda!"
    })

def create_web_app():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    return app

async def start_web_server():
    """Veb serverni orqa fonda asinxron ishga tushirish (Render va mahalliy sinov uchun)."""
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = PORT
    for attempt in range(5):
        try:
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            logger.info(f"Veb server {port}-portda muvaffaqiyatli ishga tushdi (Render uchun tayyor).")
            return runner
        except OSError as e:
            if attempt == 4:
                raise
            logger.warning(f"{port}-port band ekan ({e}), {port + 1}-port sinab ko'rilmoqda...")
            port += 1
