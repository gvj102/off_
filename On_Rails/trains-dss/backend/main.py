from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import os, sys, random
from pathlib import Path
from pydantic import BaseModel
import requests
try:
    from .models import *
except ImportError:
    from models import *

# ----------------- Models -----------------
class TrainInfo(BaseModel):
    id: str
    current_position: str
    next_station: str
    priority: int
    platform: str

class DelayRequest(BaseModel):
    trains: list[TrainInfo]
    weather_condition: str

class TrainDelay(BaseModel):
    id: str
    predicted_delay: int
    optimal_delay: int
    new_platform: str
    delay_reason: str
    scheduled_time: str

class DelayResponse(BaseModel):
    train_delays: list[TrainDelay]

# ----------------- App Setup -----------------
app = FastAPI(title="Train DSS AI")

# Frontend path
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_index():
    return FileResponse(FRONTEND_DIR / "index.html")

# ----------------- Mock Delay Model -----------------
class MockModel:
    def predict(self, df):
        return [5 for _ in range(len(df))]

delay_model = MockModel()

# ----------------- Helpers -----------------
def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

OPENWEATHER_API_KEY = "6b3468633254a6fa21b578bb8f291e0b"  # Replace with your key

# ----------------- Train Status -----------------
@app.get("/train_status")
def get_train_status(train_no: str):
    platforms = ["P1", "P2", "P3", "P4", "P5", "P6"]
    delay_reasons = ["Crossing", "Signal", "Maintenance", "Weather", "Track Issue"]

    trains = {
    "12345": [
        {"name": "Bangalore", "lat": 28.6139, "lon": 77.2090},
        {"name": "Agra", "lat": 27.1767, "lon": 78.0081},
        {"name": "Gwalior", "lat": 26.2183, "lon": 78.1828},
        {"name": "Jhansi", "lat": 25.4496, "lon": 78.5696},
        {"name": "Bhopal", "lat": 23.2599, "lon": 77.4126}
    ],
    "54321": [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
        {"name": "Solapur", "lat": 17.6599, "lon": 75.9064},
        {"name": "Kalaburagi", "lat": 17.3297, "lon": 76.8343},
        {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867}
    ],
    "17307": [
        {"name": "Kochi", "lat": 9.9312, "lon": 76.2673},
        {"name": "Thrissur", "lat": 10.5276, "lon": 76.2144},
        {"name": "Palakkad", "lat": 10.7867, "lon": 76.6548},
        {"name": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
        {"name": "Erode", "lat": 11.3410, "lon": 77.7172}
    ]
}


    if train_no not in trains:
        raise HTTPException(status_code=404, detail="Train not found")

    stations = trains[train_no]

    for s in stations:
        s["scheduled"] = random_time()

    df = pd.DataFrame([{"train_no": train_no, "station": s["name"]} for s in stations])
    predicted_delay = delay_model.predict(df)
    current_station = stations[0]

    # Fetch weather using current station coordinates
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={current_station['lat']}&lon={current_station['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(weather_url).json()
        weather_info = {
            "city": data.get("name", current_station["name"]),
            "temperature": f"{data['main']['temp']} °C",
            "condition": data["weather"][0]["description"].title(),
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s"
        }
    except:
        weather_info = {"city": current_station["name"], "temperature": "N/A", "condition": "N/A", "humidity": "N/A", "wind_speed": "N/A"}

    return {
        "train_name": f"Train {train_no}",
        "current_station": current_station["name"],
        "next_station": stations[1]["name"],
        "scheduled_arrival": current_station["scheduled"],
        "actual_arrival": current_station["scheduled"],
        "delay_minutes": random.randint(0, 15),
        "predicted_delay": int(predicted_delay[0]),
        "delay_reason": random.choice(delay_reasons),
        "platform": random.choice(platforms),
        "current_lat": current_station["lat"],
        "current_lon": current_station["lon"],
        "next_lat": stations[1]["lat"],
        "next_lon": stations[1]["lon"],
        "weather": weather_info
    }

# ----------------- Weather Endpoint -----------------
@app.get("/weather")
def get_weather(city: str = None, lat: float = None, lon: float = None):
    if city:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    elif lat is not None and lon is not None:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    else:
        raise HTTPException(status_code=400, detail="Provide city or lat/lon coordinates")
    try:
        data = requests.get(url).json()
        return {
            "city": data.get("name", "N/A"),
            "temperature": f"{data['main']['temp']} °C" if 'main' in data and 'temp' in data['main'] else "N/A",
            "condition": data["weather"][0]["description"].title() if 'weather' in data and data['weather'] else "N/A",
            "humidity": f"{data['main']['humidity']}%" if 'main' in data and 'humidity' in data['main'] else "N/A",
            "wind_speed": f"{data['wind']['speed']} m/s" if 'wind' in data and 'speed' in data['wind'] else "N/A"
        }
    except:
        return {"city": "N/A", "temperature": "N/A", "condition": "N/A", "humidity": "N/A", "wind_speed": "N/A"}

# ----------------- SOS Endpoint -----------------
@app.post("/sos")
def sos(lat: float, lon: float, category: str):
    category_map = {
        "police": "police+station",
        "hospital": "hospital"
    }
    search_category = category_map.get(category.lower(), category)
    maps_link = f"https://www.google.com/maps/search/{search_category}/@{lat},{lon},15z"
    return {
        "responder_name": f"Nearest {category.capitalize()}",
        "link": maps_link
    }

# ----------------- Delay Prediction -----------------
@app.post("/predict_delay", response_model=DelayResponse)
def predict_delay(req: DelayRequest):
    delays = []
    delay_reasons = ["Crossing", "Signal", "Maintenance", "Weather", "Track Issue"]
    platforms = ["P1", "P2", "P3", "P4", "P5", "P6"]

    for train in req.trains:
        df_in = pd.DataFrame([{
            "train_id": train.id,
            "current_station": train.current_position,
            "next_station": train.next_station,
            "priority": train.priority,
            "platform": train.platform,
            "weather": req.weather_condition
        }])
        predicted_delay = int(delay_model.predict(df_in)[0])
        random_delay = random.randint(0, 15)
        optimal_delay = max(0, random_delay - train.priority)

        delays.append(
            TrainDelay(
                id=train.id,
                predicted_delay=random_delay,
                optimal_delay=optimal_delay,
                new_platform=random.choice(platforms),
                delay_reason=random.choice(delay_reasons),
                scheduled_time=random_time()
            )
        )

    return DelayResponse(train_delays=delays)