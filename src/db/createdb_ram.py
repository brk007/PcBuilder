import csv
import os
from pymongo import MongoClient
import requests
from currency_converter import CurrencyConverter
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

import sys
sys.path.insert(1, os.getcwd() +'./src/helpers/')
import get_price

if not os.path.exists('./csv/GPU.csv'):
    import download_file as df
    df.download_csv("RAM")

if not os.path.exists('./driver/geckodriver.exe'):
    import download_file as df
    df.download_gecko_driver()

with open('./csv/RAM.csv', newline='') as f:
    reader = csv.DictReader(f)
    data = list(reader)

lists = []

for row in data:              
    gb = row["Model"].split(" ")[-1]
    gb = gb.split("GB")[0]
    
    cl= row["Model"].split(" ")[-2]
    mhz=row["Model"].split(" ")[-3]
    row["Model"] = " ".join(row["Model"].split(" ")[:-3])

    row["GB"] = str(gb)
    row["CL"] = str(cl)
    row["MHZ"] = str(mhz)
    lists.append(row)

def dict_search():
    driver = webdriver.Firefox(executable_path="./driver/geckodriver.exe")
    c = CurrencyConverter()
    price_url_base = "https://pricespy.co.uk/search?search="
    for row in data:
        if int(row["Rank"]) > 126:
            break

        full_url = price_url_base + row["Model"]
        full_url = full_url.replace(" ", "%20")
        # get models price from another script
        price = get_price.get_price(driver, c, full_url)

        if price:
            row["Price"] = price
            lists.append(row)

dict_search()

client = MongoClient('mongodb://localhost:27017/')
db = client.PcBuilder

for row in lists:
    try: 
        if row["Price"]:
            informations = {
                "Brand": row["Brand"],   
                "Model": row["Model"],
                "Rank": int(row["Rank"]),
                "Url": row["URL"],
                "Gb": row["GB"],
                "CL": row["CL"],
                "MHZ": int(row["MHZ"]),
                "Price": row["Price"]
                }
            posts = db.RAM
            post_id = posts.insert_one(informations).inserted_id
    except(KeyError):
        print("Error")


