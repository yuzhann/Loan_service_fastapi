from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class EvaluationInfo(BaseModel):
    credit_score: int
    montant_pret: str
    propriete: int


app = FastAPI()


@app.post("/analyse_risques")
async def analyse_risques(info: EvaluationInfo):
    try:
        credit_score = info.credit_score
        montant_pret = int(info.montant_pret.split(' ')[0])
        propriete = info.propriete

        if credit_score < 700:
            return {"result": False}
        elif montant_pret > 0.8 * propriete:
            return {"result": False}
        else:
            return {"result": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prise_decision")
async def prise_decision(info: EvaluationInfo):
    try:
        analyse = await analyse_risques(info)
        if analyse['result']:
            return {"decision": "Votre demande de prêt est approuvée."}
        else:
            return {"decision": "Votre demande de prêt est refusée."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# uvicorn decision:app --reload --port 8003
