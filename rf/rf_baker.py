import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


### Import train and test splits 
# Holdout year will be used for final testing once models are done
# Train
baker_train = pd.read_csv("C:/Users/sarah/Documents/GitHub/hydro_ann/baker_train.csv")
# Test
baker_val = pd.read_csv("C:/Users/sarah/Documents/GitHub/hydro_ann/baker_valid.csv")


# Remove (mostly) empty columns
baker_train = baker_train.drop(['datetime','station','st_total_rain','st_total_snow','st_total_precip','st_total_snow_on_ground','st_dir_of_max_gust_10sdeg','st_spd_of_max_gust_kmh'],axis=1)
baker_train = baker_train.dropna()
baker_val = baker_val.drop(['datetime','station','st_total_rain','st_total_snow','st_total_precip','st_total_snow_on_ground','st_dir_of_max_gust_10sdeg','st_spd_of_max_gust_kmh'],axis=1)
baker_val = baker_val.dropna()

#### ***NOTE: X and y assigned backwards! Run correctly but should probably be fixed***

# Split into met and ERA-5 datasets
baker_train_met = baker_train[['day_of_year', 'station_id', 'st_max_temp', 'st_min_temp', 'st_mean_temp', 'st_heat_deg_days', 'st_cool_deg_days']]
baker_train_era = baker_train[['day_of_year', 'station_id', 'era5_noon_t2m', 'era5_noon_evavt', 'era5_noon_ro', 'era5_noon_sd', 'era5_noon_es', 'era5_noon_sf', 'era5_noon_smlt', 'era5_noon_stl1', 'era5_noon_ssr', 'era5_noon_e', 'era5_noon_tp']]
baker_val_met = baker_val[['day_of_year', 'station_id', 'st_max_temp', 'st_min_temp', 'st_mean_temp', 'st_heat_deg_days', 'st_cool_deg_days']]
baker_val_era = baker_val[['day_of_year', 'station_id', 'era5_noon_t2m', 'era5_noon_evavt', 'era5_noon_ro', 'era5_noon_sd', 'era5_noon_es', 'era5_noon_sf', 'era5_noon_smlt', 'era5_noon_stl1', 'era5_noon_ssr', 'era5_noon_e', 'era5_noon_tp']]


# Split into X and y
baker_train_X = baker_train['flow']
baker_train_X = np.expand_dims(baker_train_X, axis=1)
baker_val_X = baker_val['flow']
baker_val_X = np.expand_dims(baker_val_X, axis=1)

'''
# Decision Tree
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score

nfolds = 5
depths = np.arange(1,21,1)
val_scores = np.zeros((depths.shape[0], nfolds))

for i, d in enumerate(depths):
  tree = DecisionTreeRegressor(max_depth=d, random_state=12)
  val_scores[i,:] = cross_val_score(tree, baker_train_X, baker_train_y, cv=nfolds, scoring='r2')

plt.figure(figsize=(12,6))
plt.plot(depths, val_scores, color='k', alpha=0.2)
plt.plot(depths, np.mean(val_scores,axis=1), color='blue')
plt.title('selecting max_depth parameter with 5-fold CV')
plt.xlabel('max_depth')
plt.ylabel('validation r-squared')
plt.xticks(depths)
plt.show()

print(np.round(np.mean(val_scores,axis=1),4))
'''


# Random Forest regression on training data
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier

variables = baker_train.columns.tolist()
print(variables)

'''
# Investigate depth selection: First 1,51,5 then within peak section of this
for depth in range(20,31,1):
  rf = RandomForestRegressor(random_state=12, max_depth=depth, max_features=0.5, oob_score=True)
  rf.fit(baker_train_met,baker_train_X)
  val_score = rf.oob_score_

  print('Met Data Random Forest (50%) validation r2 score for depth', depth,': ', np.round(rf.oob_score_,4))

for depth in range(6,16,1):
  rf = RandomForestRegressor(random_state=12, max_depth=depth, max_features=0.5, oob_score=True)
  rf.fit(baker_train_era,baker_train_X)
  val_score = rf.oob_score_

  print('ERA-5 Data Random Forest (50%) validation r2 score for depth', depth,': ', np.round(rf.oob_score_,4))
'''
# Select depths from rf validations to build models
met_depth = 8
era_depth = 12
# Met model
rf_met = RandomForestRegressor(random_state=12, max_depth=met_depth, max_features=0.5, oob_score=True)
rf_met.fit(baker_train_met,baker_train_X)
val_score = rf_met.oob_score_
print('Final Met Data Random Forest (50%) validation r2 score for depth', met_depth,': ', np.round(rf_met.oob_score_,4))
# ERA-5 model
rf_era = RandomForestRegressor(random_state=12, max_depth=era_depth, max_features=0.5, oob_score=True)
rf_era.fit(baker_train_era,baker_train_X)
val_score = rf_era.oob_score_
print('Final ERA-5 Data Random Forest (50%) validation r2 score for depth', era_depth,': ', np.round(rf_era.oob_score_,4))

# Estimate new validation data
# Met 
rf_met = RandomForestRegressor(oob_score=True, random_state=12)
rf_met.fit(baker_val_met,baker_val_X)

rf_met_val_score = rf_met.oob_score_
print('Met Data Random forest validation accuracy:', np.round(rf_met_val_score,4))

rf_met_val_pred = rf_met.predict(baker_val_met)
# ERA-5
rf_era = RandomForestRegressor(oob_score=True, random_state=12)
rf_era.fit(baker_val_era,baker_val_X)

rf_era_val_score = rf_era.oob_score_
print('ERA-5 Data Random forest validation accuracy:', np.round(rf_era_val_score,4))

rf_era_val_pred = rf_era.predict(baker_val_era)

'''
# Plot
in1=plt.plot(baker_val['date'],rf_met_val_pred)
in2=plt.plot(baker_val['date'],rf_era_val_pred)
in3=plt.plot(baker_val['date'],baker_val_X)
plt.ylabel('Discharge (m3/s)')
plt.legend([in3], ['Met','ERA-5','Measured'])
plt.legend()
plt.show()
'''

# Performance Evaluation
# R2
from sklearn.metrics import r2_score

r2_met = r2_score(baker_val_X, rf_met_val_pred)
r2_era = r2_score(baker_val_X, rf_era_val_pred)
print('R2 Met:', r2_met)
print('R2 ERA-5:', r2_era)

# RMSE, MAE, NSE
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

rmse_met = mean_squared_error(baker_val_X, rf_met_val_pred, squared=False)
rmse_era = mean_squared_error(baker_val_X, rf_era_val_pred, squared=False)
mae_met = mean_absolute_error(baker_val_X, rf_met_val_pred)
mae_era = mean_absolute_error(baker_val_X, rf_era_val_pred)

denom = np.sum((baker_val_X - np.mean(baker_val_X)) ** 2)
num_met = np.sum((rf_met_val_pred - baker_val_X) ** 2)
num_era = np.sum((rf_era_val_pred - baker_val_X) ** 2)
nse_met = 1 - num_met/denom
nse_era = 1 - num_era/denom
nnse_met = 1/(2-nse_met)
nnse_era = 1/(2-nse_era)

print("RMSE Met:", rmse_met)
print("RMSE ERA-5:",rmse_era)
print("MAE Met:", mae_met)
print("MAE ERA-5:", mae_era)
print("NSE Met:", nse_met)
print("NSE ERA-5:", nse_era)
print("NNSE Met:", nnse_met)
print("NNSE ERA-5:", nnse_era)