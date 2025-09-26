# generate_synthetic_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import random
from datetime import datetime, timedelta

# Generate synthetic dataset
trains = ["T1","T2","T3","T4","T5"]
stations = ["A","B","C","D","E"]
weather_options = ["Clear","Rain","Fog","Storm"]

data = []

for i in range(1000):
    train = random.choice(trains)
    current_station = random.choice(stations)
    next_station = random.choice([s for s in stations if s != current_station])
    sched_time = datetime(2025,9,24,8,0) + timedelta(minutes=random.randint(0,600))
    priority = random.randint(1,3)
    platform = f"P{random.randint(1,3)}"
    weather = random.choice(weather_options)
    delay_minutes = max(0, int(np.random.normal(loc=5, scale=3)))

    data.append([train, current_station, next_station, priority, platform, weather, delay_minutes])

df = pd.DataFrame(data, columns=["train_id","current_station","next_station","priority","platform","weather","delay_minutes"])

# ML model
X = df[["train_id","current_station","next_station","priority","platform","weather"]]
y = df["delay_minutes"]

categorical_features = ["train_id","current_station","next_station","platform","weather"]
preprocessor = ColumnTransformer(transformers=[("cat", OneHotEncoder(), categorical_features)])

model = Pipeline(steps=[("preprocessor", preprocessor),
                        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Save model in backend folder
joblib.dump(model, "backend/train_delay_model.pkl")
print("Model saved to backend/train_delay_model.pkl")