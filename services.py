import os
import aiohttp
import asyncio
import ast
import functools
from datetime import datetime, timedelta

from abc import ABCMeta, abstractmethod
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

from strategy import DatabaseContext, DatabaseStrategyAsyncMongoDB
# TODO: Mover a documento con solo texto.
helpGuide = "Comandos disponibles:\n\n/start - Muestra la guía de ayuda.\n/help - Muestra la guía de ayuda.\n/ayuda - Muestra la guía de ayuda.\n/status - Muestra si ha iniciado sesión o no.\n/login <usuario> <contraseña>  - Inicia sesión.\n/logout - Cierra sesión.\n/consulta <consulta> - Permite preguntar a la IA por sugerencias o órdenes."

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
    
    @classmethod
    @abstractmethod
    async def talkToAI(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    async def order(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        raise NotImplementedError
    

# Implementar interfaz de servicio.
class BotService(BotServiceInterface): 
    # session = aiohttp.ClientSession()
    # Definir contexto y pasar MongoDB estrategía.
    dbContext: DatabaseContext = DatabaseContext(DatabaseStrategyAsyncMongoDB()) 

    # Constructor
    def __init__(self):
        pass
    
    # Parametros:
    #   update,  objeto que contiene toda la información e información que proviene de Telegram (como el mensaje, o usuario que envió el comando, etc)
    #   context, contiene información sobre el estado de la librería.


    # /start /help /ayuda
    @classmethod
    async def start(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=helpGuide)

    # /status
    @classmethod
    async def status(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Consultar si ya se inicio sesión.
        result = await BotService.dbContext.exists({"chat_id": update.effective_chat.id})
        text = "Ya inició sesión." if result == True else "No ha iniciado sesión."
        # Devolver respuesta.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
    # /login <username> <password>
    @classmethod
    async def login(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        token=""
        message=""
        # Obtener parametros
        params = update["message"]["text"].split(" ")
        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]

        # Borrar mensaje.
        await context.bot.delete_message(chat_id,message_id)

        # comando <correo> <contraseña>
        if(len(params) != 3):
            message = "Ingrese su correo y contraseña. /login <correo> <contraseña>"
        else:
            # Llamar API y obtener el bearer token.
            async with aiohttp.ClientSession() as session:
                endpoint = "{}/users/login".format(os.getenv("UVICORN_API_URL"))
                async with session.post(endpoint,json={"username" : params[1], "password": params[2]}) as response:
                    # Revisar que sea HTTP 200.
                    if(response.status == 200):
                        # Remover "Bearer ".
                        token= response.headers["Authorization"].replace("Bearer ", "")
                        # Crear respuesta con nombre de usuario devuelto.
                        json = await response.json()
                        message="¡Bienvenido {}!".format(json["username"])
                        # Crear registro en base de datos si existe, de lo contrario, actualizar el existente.
                        # Cada registro contiene el ID de chat (único) y el token.
                        exists = await BotService.dbContext.exists({"chat_id": update.effective_chat.id})
                        if(exists == False):    
                            await BotService.dbContext.create({"chat_id": update.effective_chat.id, "token": token})
                        else:
                            await BotService.dbContext.update({"chat_id": update.effective_chat.id, "token": token})
                    else:
                        message = "No se pudo iniciar sesión"
        
        # Devolver respuesta.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    # /logout
    @classmethod
    async def logout(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Eliminar token correspondiente al chat.
        await BotService.dbContext.delete({"chat_id": update.effective_chat.id})
        text = "Ha cerrado sesión"
        # Devolver respuesta.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # /ai, /ia
    @classmethod
    async def talkToAI(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = ""
        reply_markup = None
        try:
            loginError="Debe iniciar sesión para poder hablar con la IA.\nUtilice el comando /login <usuario> <contraseña>"
            # Consultar si ya se inicio sesión.
            userInformation = await BotService.dbContext.get({"chat_id": update.effective_chat.id})
            if(userInformation is not None):
                # Obtener recomendación desde API
                query = update["message"]["text"].replace("/consulta ", "")
                params = {"provider":"openaiservice", "question":query}
                async with aiohttp.ClientSession() as session:
                    endpoint = "{}/unsecure/ia/ask".format(os.getenv("UVICORN_API_URL"))
                    async with session.get(endpoint, params=params) as response:
                        # TODO: Hacer API responder en JSON y no en texto (que tiene forma de JSON).
                        # Convertir respuesta que viene en texto a JSON.
                        # Y después extraer el campo "answer".
                        answer = (ast.literal_eval(await response.text()))["answer"]
                        # Revisar que sea HTTP 200.
                        if(response.status == 200):  
                            try:                      
                                print("[Resultado] [IA] [consulta] HTTP:" + str(response.status))      
                                # Intentar conseguir JSON con productos.
                                # Por cada producto, se debe mapear los campos "cantidad" por "quantity"  y crear campo "product" 
                                # para que coinicidan con los esperados por API.
                                temp = (ast.literal_eval(answer))["productos"]
                                products = list(map(lambda p: {
                                    "product": {
                                        "id":int(p["id"])
                                    }, 
                                    "quantity":p["cantidad"]
                                }, temp))

                                # Crear orden y devolver información de orden
                                additionalInformation = "Orden generada con ayuda de ChatGPT desde el bot en Telegram."
                                deliveryDate =  datetime.now()
                                order = {"orderDetails": products, "additionalInformation": additionalInformation, "deliveryDate": "{}-{}-{}".format(deliveryDate.year, deliveryDate.month, deliveryDate.day)}
                                
                                # Lista con los 3 días siguientes
                                buttons = [[InlineKeyboardButton("Cancelar",callback_data="cancel")]]
                                daysOffered = 3
                                for d in range(1,daysOffered+1):
                                    newDate = deliveryDate +timedelta(days=d)
                                    buttons.append([InlineKeyboardButton(f"{newDate.year}-{newDate.month}-{newDate.day}",callback_data=f"{newDate.year}-{newDate.month}-{newDate.day}")])
                                reply_markup = InlineKeyboardMarkup(buttons)
                                # Guardar orden en DB y enviar prompt de confirmación de fecha.
                                await BotService.dbContext.update({"chat_id": userInformation["chat_id"], "token": userInformation["token"], "order":order})
                                message = "Seleccione fecha de entrega:"
                            except (ValueError, SyntaxError) as e:
                                print("[Resultado] [recomendación].")
                                # Si no se puede parsear JSON, es una recomendación.
                                message = answer
                        elif(response.status == 403):   
                            message = loginError
                        else:
                            print("[ERROR] [IA] [orden]: Error obteniendo productos en respuesta de IA")
                            message = "De momento no puedo atender este mensaje."
            else:
                message = loginError
        except Exception as e:
            print("[ERROR] [IA]: Error obteniendo respuesta de IA")
            message = "De momento no puedo atender este mensaje."

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

    # Respuesta a selección de fecha de entrega.
    @classmethod
    async def order(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = ""
        try:
            # Obtener fecha de entrega desde respuesta.
            query = update.callback_query.data
            await update.callback_query.answer()

            # Obtener registro de usuario.
            userInformation = await BotService.dbContext.get({"chat_id": update.effective_chat.id})

            if(userInformation is not None):
                # Obtener orden desde DB.
                order = userInformation["order"]
                # Colocar fecha de entrega seleccionada en orden.
                order["deliveryDate"] = query
                # Sin importar selección eliminar orden guardada.
                await BotService.dbContext.update({"chat_id": update.effective_chat.id, "token": userInformation["token"]})

                # Elimina el teclado de selección de fecha
                await update.callback_query.edit_message_reply_markup(None)    

                # Si se selecciona una fecha, se crea la orden.
                if(query != "cancel"):
                    # Realzar orden.
                    endpoint = "{}/order".format(os.getenv("UVICORN_API_URL"))
                    headers={"Authorization" : "Bearer {}".format(userInformation["token"])}
                    async with aiohttp.ClientSession() as session:
                        async with session.post(endpoint, json=order, headers=headers) as response:
                            print("[Resultado] [orden] HTTP:" + str(response.status))
                            responseJSON = await response.json()
                            # Mostrar orden de manera que el usuario la pueda leer.
                            deliveryDateResponse = datetime.strptime(responseJSON["deliveryDate"], "%Y-%m-%dT%H:%M:%S.%f%z")
                            dateResponse = datetime.strptime(responseJSON["date"], "%Y-%m-%dT%H:%M:%S.%f%z")
                            
                            message= "Tiquete de compra: N°{}\nFecha de compra: {}\nFecha de entrega: {}\n\nTotal: {}\nInformación adicional: {}\n\nDetalles:\n".format(responseJSON["id"], dateResponse.strftime("%Y-%m-%d"), deliveryDateResponse.strftime("%Y-%m-%d"), responseJSON["total"], responseJSON["additionalInformation"])
                            
                            details = list(map(lambda detail : "Cantidad: {} || Producto:{} || Total: {}\n".format(detail["quantity"],detail["product"]["name"],detail["total"]), responseJSON["orderDetails"]))
                            for detail in details:
                                message = message + detail
                            message = message + "\n¡Gracias por comprar!"
                    # Ajustar mensaje previo (donde se coloca el teclado).
                    await update.callback_query.edit_message_text(f"Seleccionó {query} como fecha de entrega.")
                else:
                    await update.callback_query.edit_message_text("Se ha cancelado la orden.")
            else:
                message = "Debe iniciar sesión para poder comprar."
        except Exception as e:
            print("[ERROR] [orden]: Error realizando orden")
            message = "De momento no puedo atender este mensaje."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
