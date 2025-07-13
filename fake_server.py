from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running (fake server for Render)")

def start_fake_server():
    app = web.Application()
    app.router.add_get('/', handle)
    web.run_app(app, port=8080)
