import os
from datetime import datetime

MONGO_URI = os.environ.get('MONGO_URI')

if MONGO_URI:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()

    def init_db():
        # Ensure indexes
        db.users.create_index('email', unique=True)
        db.entries.create_index('patient_id')

    def create_user(email, password_hash, role='patient'):
        user = {'email': email, 'password': password_hash, 'role': role}
        res = db.users.insert_one(user)
        return str(res.inserted_id)

    def get_user_by_email(email):
        return db.users.find_one({'email': email})

    def create_entry(patient_id, filename, narrative, timestamp=None):
        doc = {'patient_id': patient_id, 'filename': filename, 'narrative': narrative, 'timestamp': timestamp or datetime.utcnow()}
        res = db.entries.insert_one(doc)
        return str(res.inserted_id)

    def list_entries_for_patient(patient_id):
        return list(db.entries.find({'patient_id': patient_id}))

    def list_all_entries():
        return list(db.entries.find())

    def get_entry(entry_id):
        from bson import ObjectId
        return db.entries.find_one({'_id': ObjectId(entry_id)})

    def delete_entry(entry_id):
        from bson import ObjectId
        db.entries.delete_one({'_id': ObjectId(entry_id)})

    def update_entry(entry_id, **kwargs):
        from bson import ObjectId
        db.entries.update_one({'_id': ObjectId(entry_id)}, {'$set': kwargs})

else:
    # TinyDB fallback
    from tinydb import TinyDB, Query
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    tdb = TinyDB(DB_PATH)
    users = tdb.table('users')
    entries = tdb.table('entries')
    UserQ = Query()

    def init_db():
        pass

    def create_user(email, password_hash, role='patient'):
        user = {'email': email, 'password': password_hash, 'role': role}
        return users.insert(user)

    def get_user_by_email(email):
        res = users.search(UserQ.email == email)
        return res[0] if res else None

    def create_entry(patient_id, filename, narrative, timestamp=None):
        doc = {'patient_id': patient_id, 'filename': filename, 'narrative': narrative, 'timestamp': (timestamp or datetime.utcnow()).isoformat()}
        return entries.insert(doc)

    def list_entries_for_patient(patient_id):
        return entries.search(Query().patient_id == patient_id)

    def list_all_entries():
        return entries.all()

    def get_entry(entry_id):
        return entries.get(doc_id=entry_id)

    def delete_entry(entry_id):
        entries.remove(doc_ids=[entry_id])

    def update_entry(entry_id, **kwargs):
        entries.update(kwargs, doc_ids=[entry_id])
