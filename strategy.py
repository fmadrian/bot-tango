# Patrón tomado de: https://refactoring.guru/design-patterns/strategy/python/example
from __future__ import annotations
import os
from abc import ABC, abstractmethod
from bson import ObjectId
import motor.motor_asyncio


class DatabaseContext():
    """
    The Context defines the interface of interest to clients.
    """

    def __init__(self, strategy: DatabaseStrategy) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._strategy = strategy

    @property
    def strategy(self) -> DatabaseStrategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: DatabaseStrategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """
        self._strategy = strategy

    async def create(self,data):
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        await self._strategy.create(data)

    async def get(self,data):
        await self._strategy.get(data)

    async def update(self,data):
        await self._strategy.update(data)

    async def delete(self,data):
        await self._strategy.delete(data)


class DatabaseStrategy(ABC):
    """
    The Strategy interface declares operations common to all supported versions
    of some algorithm.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """

    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def update(self, data):
        pass

    @abstractmethod
    def get(self, data) -> bool:
        pass

    @abstractmethod
    def delete(self, data):
        pass

"""
Concrete Strategies implement the algorithm while following the base Strategy
interface. The interface makes them interchangeable in the Context.
"""

class DatabaseStrategyAsyncMongoDB(DatabaseStrategy):

    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("UVICORN_MONGODB_CONNECTION_STRING"))
    db = client["tango"]
    collection = db["sessions"]


    async def create(self, data):
        # Crear registro en base de datos si existe, de lo contrario, actualizar el existente.
        exists = await self.get({"chat_id": data["chat_id"]})
        if(exists == False):
            await DatabaseStrategyAsyncMongoDB.collection.insert_one({"_id": ObjectId(), "chat_id": data["chat_id"], "key": data["key"]})
        else:
            await self.update(data)

    async def update(self, data):
        query = { "chat_id": data["chat_id"] }
        values = { "$set": { "key": data["key"] } }
        await DatabaseStrategyAsyncMongoDB.collection.update_one(query, values)

    async def get(self, data):
        result = await DatabaseStrategyAsyncMongoDB.collection.find_one(data)
        print(result != None)
        return result != None 
    
    async def delete(self, data):
         await DatabaseStrategyAsyncMongoDB.collection.delete_one(data)


"""
# No sirve estrategía porque no es asíncrona.
class DatabaseStrategyMongoDB(DatabaseStrategy):

    client: MongoClient = MongoClient(os.getenv("UVICORN_MONGODB_CONNECTION_STRING"))
    db: Database = client.get_database("tango")
    collection: Collection = db.get_collection("sessions")

    def create(self, data):
        # Crear registro en base de datos si existe, de lo contrario, actualizar el existente.
        exists = self.get({"chat_id": data["chat_id"]})
        if(exists == False):
            DatabaseStrategyMongoDB.collection.insert_one({"_id": ObjectId(), "chat_id": data["chat_id"], "key": data["key"]})
        else:
            self.update(data)

    def update(self, data):
        query = { "chat_id": data["chat_id"] }
        values = { "$set": { "key": data["key"] } }
        DatabaseStrategyMongoDB.collection.update_one(query, values)
        pass

    def get(self, data):
        result = DatabaseStrategyMongoDB.collection.find_one(data)
        print(result != None)
        return result != None 

    def delete(self, data):
        DatabaseStrategyMongoDB.collection.delete_one(data)
        pass
"""