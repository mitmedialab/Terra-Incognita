import csv
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
reader = csv.DictReader(open(os.path.join(BASE_DIR,"static/data/1000cities.csv"),'rU'))
THE1000CITIES = [row for row in reader]

THE1000CITIES_IDS_ARRAY = []
for row in THE1000CITIES:
	if "geonames_id" in row.keys() and len(row["geonames_id"]) > 0:
		THE1000CITIES_IDS_ARRAY.append(int(row["geonames_id"]))
