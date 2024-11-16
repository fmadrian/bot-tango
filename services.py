from abc import ABCMeta, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

from strategy import DatabaseContext, DatabaseStrategyAsyncMongoDB
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
    async def login(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    async def logout(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError
    

# Implement interface.
class BotService(BotServiceInterface): 
    # Definir contexto y pasar MongoDB estrategía.
    context: DatabaseContext = DatabaseContext(DatabaseStrategyAsyncMongoDB()) 

    # Constructor
    def __init__(self):
        pass
    
    # Parameters:
    #   update,  objeto que contiene toda la información e información que proviene de Telegram (como el mensaje, o usuario que envió el comando, etc)
    #   context, contiene información sobre el estado de la librería.

    # /start
    @classmethod
    async def start(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=helpGuide)

    # /status
    @classmethod
    async def status(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Consultar si ya se inicio sesión.
        result = BotService.context.get({"chat_id": update.effective_chat.id})
        text = "Ya inició sesión." if result == True else "No ha iniciado sesión."
        # Devolver respuesta.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
    @classmethod
    async def login(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Llamar API y obtener el token.
        bearerToken="example"
        # Guardar token.
        await BotService.context.create({"chat_id": update.effective_chat.id, "key": bearerToken})
        text = "Ha iniciado sesión"
        # Devolver respuesta.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    @classmethod
    async def logout(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Consultar si ya se inicio sesión.
        result = BotService.context.delete({"chat_id": update.effective_chat.id})
        text = "Ha cerrado sesión"
        # Devolver respuesta.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)