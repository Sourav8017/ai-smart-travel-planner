import joblib

model = joblib.load("ml/travel_model.pkl")

def predict_score(rating):
    prediction = model.predict([[rating]])
    return int(prediction[0])
