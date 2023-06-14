import requests
import re
from bs4 import BeautifulSoup
import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
log_file_name = "log.txt"
file_name = "cars.json"
telegram_token = os.getenv('telegram_token')
chat_id = os.getenv('chat_id')
delay = 300/1000 #ms
domain = "https://www.bazaraki.com" 

#Car object
class Car(object):
    def __init__(self, model, carId, src, name, details, price, date, place, link):
        self.model = model
        self.carId = carId
        self.src = src
        self.name = name
        self.details = details
        self.price = price
        self.date = date
        self.place = place
        self.link = link

#GET URL description for searching specific types car
class SearchCarType(object):
    def __init__(self, model, url, description):
        self.model = model
        self.url = url
        self.description = description

#Defining search requests
searchCarTypes = [
    SearchCarType(
        "Volkswagen Eos",
        "https://www.bazaraki.com/car-motorbikes-boats-and-parts/cars-trucks-and-vans/volkswagen/eos/gearbox---1/",
        "Volkswagen Eos, auto"
    ),
]

#Load existing cars information from the file
def loadExistingCarIdsFromFile():
    existingCarIds = []
    with open(file_name) as f:
        for line in f:
            existingCarIds.append(json.loads(line)["carId"])
    return existingCarIds
def saveCarToFile(carObj):
        jsonCar = json.dumps(carObj.__dict__)
        #Append to the file
        with open(file_name, 'a') as file:
            file.write(jsonCar + "\n")
def send_message(car):
    if(car.carId not in loadExistingCarIdsFromFile()):
        msg = f"🚙 {car.name}\n\n<b>Date:</b> {car.date}\n<b>Location</b>: {car.place}\n<b>Details</b>: {car.details}\n<b>Price</b>: {car.price} EUR\n\nMore details <a href='{domain}{car.link}'>here</a>"
        img_uri = car.src
        telegram_msg = requests.get(f'https://api.telegram.org/bot{telegram_token}/sendPhoto?chat_id={chat_id}&caption={msg}&photo={img_uri}&parse_mode=html')
        saveCarToFile(car)
        time.sleep(delay)
foundCarAmount = 0
#Parse data
for carType in searchCarTypes:
    #Request information about all types of specific car type
    vgm_url = carType.url
    html_text = requests.get(vgm_url).text
    time.sleep(delay)
    soup = BeautifulSoup(html_text, 'html.parser')
    #Get all cars
    cars = soup.find_all('li',attrs={"class": "announcement-container"})
    for car in cars:
        link = car.find("a", attrs={"itemprop": "url"})["href"]
        carId = link.split("/")[2]

        src = car.find("img")["src"]
        name = car.find("img")["alt"]
        details = car.find("div", attrs={"class": "announcement-block__description"}).get_text()
        price = car.find("meta", attrs={"itemprop": "price"})["content"].split(".")[0]
        
        dateAndPlaceWithEmptyLines = car.find("div", attrs={"class": "announcement-block__date"}).get_text()
        #Remove empty lines
        dateAndPlace = "".join([s for s in dateAndPlaceWithEmptyLines.splitlines(True) if s.strip()])
        dateAndPlace = re.sub(' +', ' ', dateAndPlace)[1:]
        date = dateAndPlace.splitlines()[0][:-1]
        place = dateAndPlace.splitlines()[1][1:]
        
        #Create object and transform it to a json structure
        carObj = Car(carType.model, carId, src, name, details, price, date, place, link)
        foundCarAmount = foundCarAmount + 1
        send_message(carObj)

log = f"{datetime.today()} | Found {foundCarAmount} cars"
with open(log_file_name, 'a') as file:
    file.write(log + "\n")