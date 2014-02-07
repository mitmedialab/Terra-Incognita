# A script to convert geocodes from multiple files into one CSV file
# Shouldn't need to be run now that I have the file so you can just 
# disregard this
import csv

COUNTRIES = list(csv.DictReader(open("static/data/geodata/countries_to_regions.csv",'rU')))
REGIONS = list(csv.DictReader(open("static/data/geodata/regions_to_continents.csv",'rU')))
CONTINENTS = list(csv.DictReader(open("static/data/geodata/continents.csv",'rU')))

test_file = open('ALL_GEO.csv','wb')
fieldnames = ["un_country_code", "country_name", "country_code","region_code", "region_name", "continent_code", "continent_name"]
csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
csvwriter.writeheader()

for row in COUNTRIES:
	new_row = row.copy()
	print "now on " + row["country_name"]
	for row_inner in REGIONS:
		print "region now on " + row_inner["region_name"]
		if row_inner["region_code"] == row["region_code"]:
			new_row["region_name"] = row_inner["region_name"]
			
			new_row["continent_code"] = row_inner["continent_code"]
			for row_inner_inner in CONTINENTS:
				print "continent now on " + row_inner_inner["name"]
				if row_inner["continent_code"] == row_inner_inner["continent_code"]:
					new_row["continent_name"] = row_inner_inner["name"]
					csvwriter.writerow(new_row)
					break
			break
