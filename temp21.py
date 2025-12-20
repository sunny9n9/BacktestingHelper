import os
import re
import json
from datetime import datetime
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

########### FETCH FETCH FETCH ##########
pattern = re.compile(r"^nifty_options_(\d{8})_(\d{6})\.json$")

folder_path = "nse_option_chain_data"
files = []
for fname in os.listdir(folder_path):
    match = pattern.match(fname)
    if match:
        date_str, time_str = match.groups()
        files.append((fname, date_str, time_str))

files.sort(key=lambda x: (x[1], x[2]))

print(f"Total files found: {len(files)}")

def flatten_snapshot(snapshot_time, snapshot_json):
    rows = []
    for strike_data in snapshot_json["records"]["data"]:
        for opt_type in ["CE", "PE"]:
            if opt_type in strike_data:
                opt = strike_data[opt_type]
                row = {
                    "releasetime": snap_json['records']['timestamp'],
                    "recordtime": snapshot_time,
                    "expiryDate": datetime.strptime(opt["expiryDate"], "%d-%m-%Y"),
                    "strikePrice": opt["strikePrice"],
                    "optionType": opt_type,
                    "openInterest": float(opt["openInterest"]),
                    "changeinOpenInterest": float(opt["changeinOpenInterest"]),
                    "totalTradedVolume": float(opt["totalTradedVolume"]),
                    "impliedVolatility": float(opt["impliedVolatility"]),
                    "lastPrice": float(opt["lastPrice"]),
                    "buyPrice1": float(opt["buyPrice1"]),
                    "sellPrice1": float(opt["sellPrice1"]),
                    "buyQuantity1": int(opt["buyQuantity1"]),
                    "sellQuantity1": int(opt["sellQuantity1"]),
                    "underlyingValue": float(opt["underlyingValue"])
                }
                rows.append(row)
    return rows
all_rows = []
date_set = set()  # track unique dates

for fname, date_str, time_str in files:
    file_dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
    # the above function tells python the format of datetime and pass datetime
    date_set.add(date_str)

    with open(os.path.join(folder_path, fname), "r") as f:
        snap_json = json.load(f)

    all_rows.extend(flatten_snapshot(file_dt, snap_json))
df = pd.DataFrame(all_rows)
df.set_index(["recordtime", "strikePrice", "optionType"], inplace=True)
df.sort_index(inplace=True)

print(f"Unique dates in dataset: {sorted(date_set)}")
print(df.head())

print(len(df.columns))

########## EDA EDA EDA ##########


