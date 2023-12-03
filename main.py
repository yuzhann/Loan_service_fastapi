import asyncio
import httpx
import requests


async def send_data_to_ieservice(text):
    url = "http://127.0.0.1:8000/identify_entities"
    data = {"text": text}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)

    print("Response status code:", response.status_code)
    print("Response content:", response.text)

    return response.json()

if __name__ == '__main__':
    text_to_analyze = """
    #         Nom du client: John Doe
    #         Adresse: 123 Rue de la Liberté, 75001 Paris, France
    #         Email: john.doe@email.com
    #         Numéro de téléphone: +33 123 456 789
    #         Montant du Prêt Demandé: 200000 EUR
    #         Durée du Prêt: 20 ans
    #         Description de la Propriété: Maison à deux étages avec jardin, située dans un quartier résidentiel calme.
    #         Revenu Mensuel: 5000 EUR
    #         Dépenses Mensuelles: 3000 EUR
    #         """
    asyncio.run(send_data_to_ieservice(text_to_analyze))



