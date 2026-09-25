import logging
from aiohttp import web
from config import PORT

logger = logging.getLogger(__name__)

async def handle_ping(request):
    """Render uchun Health Check / Ping endpoint."""
    return web.json_response({
        "status": "online",
        "service": "Telegram Music Bot",
        "username": "@musiqazuxibot"
    })

def create_web_app():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    return app

async def start_web_server():
    """Veb serverni orqa fonda asinxron ishga tushirish."""
    app = create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Veb server {PORT}-portda muvaffaqiyatli ishga tushdi (Render uchun tayyor).")
    return runner
