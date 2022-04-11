## How to create a JSON file?

**Detail of the JSON file** 

Below is a template of the JSON file. JSON is an open standard file format an data interchange format that uses human-readable text to store and transmit data object. You can click [here](https://en.wikipedia.org/wiki/JSON) to find more information of JSON.

```python
{
"city_loc": {"lat": 40.1164, "lon": -88.2434}, 
"catalog_url": "https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json", 
"l_component": "lnd",
"a_component": "atm",
"experiment": "RCP85",
"frequency": "daily",
"cam_ls": ["TREFHT", "TREFHTMX", "FLNS", "FSNS", "PRECSC", "PRECSL", "PRECT", "QBOT", "UBOT", "VBOT"], 
"clm_ls": ["TREFMXAV_U"], 
"time_start": "2081-01-02", 
"time_end": "2100-12-31", 
"member_id": [2], 
"estimator_list": ["lgbm", "xgboost", "rf", "extra_tree"], 
"time_budget": 15, 
"features": ["FLNS", "FSNS", "PRECT", "PRSN", "QBOT", "TREFHT", "UBOT", "VBOT"], 
"label": ["TREFMXAV_U"]
}
```

where

```
city_loc : dict
    a dict of a city's lat and lon that we are interested in , e.g., {'lat': 40.1164, 'lon': -88.2434}
catalog_url : string, optional
    catalog URL, by default cesm1_catalog_url ('https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json')
l_component : str, optional
    component name of CLM, by default "lnd"
a_component : str, optional
    component name of CAM, by default "atm"         
experiment : string
    e.g., "RCP85" (RCP 8.5 runs)
frequency : string
    e.g., "daily" or "monthly"
cam_ls : a list of string
    CAM (atmospheric forcing) variables, e.g., ["TREFHT", "TREFHTMX", "FLNS", "FSNS"]
clm_ls : a list of string
    CLM (land) variables, e.g., ["TREFMXAV_U"] (Urban daily maximum of average 2-m temperature) 
time_start: string
    start date, e.g., "2081-01-02"
time_end: string
    end date, e.g., "2100-12-31"
member_id : a list of int
    CESM1 large ensemble member ID, e.g., [2,3]
estimator_list : a list of string
    a list of strings for estimator names, e.g., ["lgbm", "xgboost", "rf", "extra_tree"], or 'auto'
time_budget : int
    total running time in seconds, e.g., 15
features : a list of string
    features (predictors) for machine learning, it should be a subset of "cam_ls"
label: a list of string (currently we only support a single element within the list)
    label for machine learning, "label" means something we want to predict, e.g., ["TREFMXAV_U"]
```

**How to create a JSON file using Python**

```python
import json
data = {
    "city_loc": {"lat": 40.1164, "lon": -88.2434}, 
    "catalog_url": "https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json", 
    "l_component": "lnd",
    "a_component": "atm",
    "experiment": "RCP85",
    "frequency": "daily",
    "cam_ls": ["TREFHT", "TREFHTMX", "FLNS", "FSNS", "PRECSC", "PRECSL", "PRECT", "QBOT", "UBOT", "VBOT"], 
    "clm_ls": ["TREFMXAV_U"], 
    "time_start": "2081-01-02", 
    "time_end": "2100-12-31", 
    "member_id": [2], 
    "estimator_list": ["lgbm", "xgboost", "rf", "extra_tree"], 
    "time_budget": 15, 
    "features": ["FLNS", "FSNS", "PRECT", "PRSN", "QBOT", "TREFHT", "UBOT", "VBOT"], 
    "label": ["TREFMXAV_U"]
}

# The file is save at current working directory, with a file name "config.json"
with open('./config.json', 'w') as outfile:
    #json_string = json.dumps(data)
    json.dump(data, outfile)
```

**How to load a JSON file using Python**

```python
with open("./config.json",'r') as load_f:
    param = json.load(load_f)
```



Last update: Zhonghua Zheng, 2022/03/21

