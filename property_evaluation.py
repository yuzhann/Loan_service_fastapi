from fastapi import FastAPI, HTTPException



class PropertyEvaluationDatabase:
    data = {
        "Appt-001": {"codePostal": 75001, "prix": 500000},  # Estimated market price in EUR based on the address
        "Appt-002": {"codePostal": 75001, "prix": 600000},
        "Appt-003": {"codePostal": 75001, "prix": 550000}
    }

    @classmethod
    def get_prices_by_code_postal(cls, code_postal):
        """Find property prices of the given code postal"""
        prices = [info["prix"] for info in cls.data.values() if info["codePostal"] == code_postal]
        return prices


class MarketDataAnalysis:
    @staticmethod
    def analyse_property_market_data(prices):
        """Estimate the value of the property based on recent sales of similar properties."""
        average_price = sum(prices) / len(prices) if prices else 0

        return average_price


app = FastAPI()


@app.post("/evaluate_property_value/{codePostal}")
async def evaluate_property_value(codePostal: str):
    try:
        prices = PropertyEvaluationDatabase.get_prices_by_code_postal(codePostal)
        market_value = MarketDataAnalysis.analyse_property_market_data(prices)
        print(codePostal)

        client_data = {
            "Property": market_value
        }
        return client_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






# uvicorn property_evaluation:app --reload --port 8088
# http://127.0.0.1:8088

