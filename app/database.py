from pymongo import MongoClient

from .config import DATABASE_NAME, MONGO_URI


client = None
db = None


class _CollectionProxy:
	def __init__(self) -> None:
		self._collection = None

	def set_collection(self, collection) -> None:
		self._collection = collection

	def __getattr__(self, name):
		if self._collection is None:
			raise RuntimeError("Database has not been initialized yet")
		return getattr(self._collection, name)

	def __getitem__(self, key):
		if self._collection is None:
			raise RuntimeError("Database has not been initialized yet")
		return self._collection[key]


users_collection = _CollectionProxy()
images_collection = _CollectionProxy()


def init_database() -> None:
	global client, db
	client = MongoClient(MONGO_URI)
	db = client[DATABASE_NAME]
	users_collection.set_collection(db["users"])
	images_collection.set_collection(db["images"])


def close_database() -> None:
	global client, db
	if client is not None:
		client.close()
	client = None
	db = None
