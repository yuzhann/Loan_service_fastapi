from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import re
import httpx


def extract_info(pattern, text, default=""):
    match = pattern.search(text)
    return match.group() if match else default

# Generate id client
class IDGenerator:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.current_id = self.load_last_id()

    def load_last_id(self):
        id_record = self.collection.find_one({}, sort=[('_id', -1)])

        if id_record and 'last_id' in id_record:
            return id_record['last_id']
        else:
            return 0

    def get_new_id(self):
        # update id
        self.current_id += 1
        new_id = self.current_id

        # add new id to database
        self.collection.update_one({}, {'$set': {'last_id': new_id}}, upsert=True)

        return str(new_id).zfill(3)

# Get id client from mongodb
def get_client_id():
    MONGO_URI = 'mongodb://localhost:27017/'
    DB_NAME = "client_info"
    COLLECTION_NAME = "id"

    id_generator = IDGenerator(mongo_uri=MONGO_URI, db_name=DB_NAME, collection_name=COLLECTION_NAME)

    new_id = id_generator.get_new_id()
    return new_id


app = FastAPI()


class TextRequest(BaseModel):
    text: str


@app.post("/identify_entities")
async def identify_entities(request: TextRequest):
    text = request.text
    name_pattern = re.compile(r'Nom du client:\s*(.*)')
    address_pattern = re.compile(r'Adresse:\s*(.*)')
    code_postal_pattern = re.compile(r'Adresse:.*?(\d{5})')
    email_pattern = re.compile(r'Email:\s*([\w\.-]+@[\w\.-]+\.\w+)')
    phone_pattern = re.compile(r'Numéro de téléphone:\s*(\+\d{1,3}\s?\d{1,4}\s?\d{3}\s?\d{3})')
    montant_pattern = re.compile(r'Montant du Prêt Demandé:\s*([\d\s]+EUR)')
    duree_pattern = re.compile(r'Durée du Prêt:\s*(.*)')
    description_pattern = re.compile(r'Description de la Propriété:\s*(.*)')
    revenu_pattern = re.compile(r'Revenu Mensuel:\s*([\d\s]+EUR)')
    depenses_pattern = re.compile(r'Dépenses Mensuelles:\s*([\d\s]+EUR)')

    data = {
        'Client_id': get_client_id(),
        'Nom du client': name_pattern.search(text).group(1).strip(),
        'Adresse': address_pattern.search(text).group(1).strip(),
        'Code_Postal': code_postal_pattern.search(text).group(1).strip(),
        'Email': email_pattern.search(text).group(1).strip(),
        'Numéro de téléphone': phone_pattern.search(text).group(1).strip(),
        'Montant du Prêt Demandé': montant_pattern.search(text).group(1).strip(),
        'Durée du Prêt': duree_pattern.search(text).group(1).strip(),
        'Description de la Propriété': description_pattern.search(text).group(1).strip(),
        'Revenu Mensuel': revenu_pattern.search(text).group(1).strip(),
        'Dépenses Mensuelles': depenses_pattern.search(text).group(1).strip()
    }
    mongodb_client = MongoClient('localhost', 27017)
    db = mongodb_client['client_info']
    coll = db["info"]
    coll.insert_one(data)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://127.0.0.1:8088/evaluate_property_value/{data['Code_Postal']}")
        property_value = response.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://127.0.0.1:8002/check_solvency/{data['Client_id']}")
        solvency_status = response.json()

    info = {
        "credit_score": int(solvency_status["credit_score"]),
        "montant_pret": data['Montant du Prêt Demandé'],
        "propriete": int(property_value["Property"])
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://127.0.0.1:8003/prise_decision", json=info)
        result = response.json()

    return result

# uvicorn IEService:app --reload
# http://127.0.0.1:8000
