# Train a simple ETA baseline model using scikit-learn
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib

# Read positions and trains
pos = pd.read_csv('positions.csv', parse_dates=['timestamp'])
trains = pd.read_csv('trains.csv', parse_dates=['scheduled_departure','scheduled_arrival'])

# simple feature engineering: per train last speed and time-from-start
pos = pos.sort_values(['train_id','timestamp'])
pos['t0'] = pos.groupby('train_id')['timestamp'].transform('min')
pos['sec_from_start'] = (pos['timestamp'] - pos['t0']).dt.total_seconds()

# compute target: seconds remaining to last known record per train
last = pos.groupby('train_id')['sec_from_start'].transform('max')
pos['remaining_seconds'] = last - pos['sec_from_start']

# use last record per train as sample
last_records = pos.groupby('train_id').tail(1)

X = last_records[['sec_from_start','speed_kmph']]
Y = last_records['remaining_seconds']

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
model = GradientBoostingRegressor(n_estimators=200, max_depth=4)
model.fit(X_train, y_train)
print('Baseline ETA model trained. Test R2:', model.score(X_test,y_test))
joblib.dump(model, 'eta_baseline.joblib')
print('Saved model to eta_baseline.joblib')