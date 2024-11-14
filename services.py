import os
from abc import ABCMeta, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

# TODO: Mover a documento con solo texto.
helpGuide = "Hola!"

# Interfaz
class BotServiceInterface(metaclass=ABCMeta):
    
    @classmethod
    @abstractmethod
    async def start(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    async def talkToAI(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError

# Implement interface.
class BotService(BotServiceInterface): 

    def __init__(self):
        pass
    
    # Parameters:
    #   update,  objeto que contiene toda la información e información que proviene de Telegram (como el mensaje, o usuario que envió el comando, etc)
    #   context, contiene información sobre el estado de la librería.

    # /start
    @classmethod
    async def start(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=helpGuide)

    # /reco Recomendación desde el AI
    @classmethod
    async def talkToAI(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
