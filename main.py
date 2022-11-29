import sqlite3

from config import settings
from data import SQLRepository
from fastapi import FastAPI
from pydantic import BaseModel


# Task 8.4.14, `FitIn` class
class FitIn(BaseModel):
    ticker: str
    use_new_data: bool
    n_observations: int
    p: int
    q:int

# Task 8.4.14, `FitOut` class
class FitOut(FitIn):
    success: bool
    message: str

# Task 8.4.18, `PredictIn` class
class PredictIn(BaseModel):
    ticker: str
    n_days: str


# Task 8.4.18, `PredictOut` class
class PredictOut(PredictIn):
    success: bool
    forecast: dict
    message: str


# Task 8.4.9
app = FastAPI()


# Task 8.4.11
# `"/hello" path with 200 status code
@app.get("/hello", status_code=200)
def hello():
    """Return dictionary with greeting message."""
    return {"message": "Hello world!"}



# Task 8.4.16, `"/fit" path, 200 status code
@app.post("/fit", status_code=200, response_model = FitOut)
def fit_model(request: FitIn):

    """Fit model, return confirmation message.

    Parameters
    ----------
    request : FitIn

    Returns
    ------
    dict
        Must conform to `FitOut` class
    """
    # Create `response` dictionary from `request`
    response = request.dict()
    
    # Create try block to handle exceptions
    try:
        # Build model with `build_model` function

        # Wrangle data
        model.wrangle_data(n_observations = request.n_observations)

        # Fit model
        model.fit(p=request.p,q=request.q)

        # Save model
        filename=model.dump()

        # Add `"success"` key to `response`
        response["success"] = True

        # Add `"message"` key to `response` with `filename`
        response["message"] = f"model train and saved {filename}"

    # Create except block
    except Exception as e:
        
        # Add `"success"` key to `response`
        response["success"] = False

        # Add `"message"` key to `response` with error message
        response["message"] = str(e)

    # Return response
    return response


# Task 8.4.19 `"/predict" path, 200 status code
@app.post("/predict", status_code=200, response_model = PredictOut)
def get_prediction(request: PredictIn):

    # Create `response` dictionary from `request`
    response = request.dict()

    # Create try block to handle exceptions
    try:
        # Build model with `build_model` function
        model = build_model(ticker = request.ticker,use_new_data=False)

        # Load stored model
        model.load()

        # Generate prediction
        prediction = model.predict_volatility(horizon = request.n_days)

        # Add `"success"` key to `response`
        response["success"] = True
        
        response["forecast"] = prediction
        # Add `"message"` key to `response` with `filename`
        response["message"] = ""

    # Create except block
    except Exception as e:
        
        # Add `"success"` key to `response`
        response["success"] = False
        response["forecast"] = {}
        # Add `"message"` key to `response` with error message
        response["message"] = str(e)


    # Return response
    return response
