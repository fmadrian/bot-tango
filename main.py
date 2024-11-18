import os
# Local imports
from services import BotService
# Other imports
from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler
from fastapi import FastAPI, Request, Response

# Desplegar un webhook al cual Telegram enviará los mensajes recibidos.

TELEGRAM_WEBHOOK_URL= "https://api.telegram.org/bot{}/setWebhook?url={}".format(os.getenv("UVICORN_TELEGRAM_BOT_TOKEN"), os.getenv("UVICORN_WEBHOOK_HOST"))
# Initializar el bot.
ptb = (
    Application.builder()
    .updater(None)
    .token(os.getenv("UVICORN_TELEGRAM_BOT_TOKEN"))
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await ptb.bot.setWebhook(TELEGRAM_WEBHOOK_URL)
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

# Initializar el webhook (FastAPI app)
app = FastAPI(lifespan=lifespan)

# Endpoint que maneja los requests hechos al webhook.
@app.post("/")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

# Añadir los diferentes tipos de eventos que el bot maneja.
ptb.add_handler(CommandHandler("start", BotService.start))
ptb.add_handler(CommandHandler("help", BotService.start))
ptb.add_handler(CommandHandler("ayuda", BotService.start))
ptb.add_handler(CommandHandler("status", BotService.status))
ptb.add_handler(CommandHandler("login", BotService.login))
ptb.add_handler(CommandHandler("logout", BotService.logout))
ptb.add_handler(CommandHandler("ai", BotService.talkToAI))
ptb.add_handler(CommandHandler("ia", BotService.talkToAI))
ptb.add_handler(CallbackQueryHandler(BotService.order))