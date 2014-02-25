# A script to write country codes into a geo CSV file of cities which only keys
# on country names
import csv
import difflib

CITIES = list(csv.DictReader(open("cities_temp.csv",'rU')))
COUNTRIES = list(csv.DictReader(open("countries_temp.csv",'rU')))
countriesCovered = []
test_file = open('cities_new.csv','wb')
fieldnames = ["country_name", "city1", "city2","country_code", "un_country_code","region_code", "region_name", "continent_code", "continent_name","citation"]
csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
csvwriter.writeheader()

for row in CITIES:
	new_row = row.copy()
	
	for row_inner in COUNTRIES:
		if difflib.SequenceMatcher(None, row_inner["country_name"], row["country_name"]).ratio() > 0.8:
			print row_inner["country_name"] + " matches " + row["country_name"]
			
			new_row["country_name"] = row_inner["country_name"]
			new_row["country_code"] = row_inner["country_code"]
			new_row["un_country_code"] = row_inner["un_country_code"]
			new_row["region_code"] = row_inner["region_code"]
			new_row["region_name"] = row_inner["region_name"]
			new_row["continent_code"] = row_inner["continent_code"]
			new_row["continent_name"] = row_inner["continent_name"]
			countriesCovered.append(row_inner["country_code"])
			csvwriter.writerow(new_row)
			break
	
missing =0
for row in COUNTRIES:
	new_row = row.copy()
	if row["country_code"] not in countriesCovered:
		print "NO " + row["country_name"]
		new_row["city1"]=""
		new_row["city2"]=""
		missing+=1
		csvwriter.writerow(new_row)
print "Missing: " + str(missing)