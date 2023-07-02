from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3

import requests, json



# Définition de la fonctionnalité - mise à jour database

def updateRestaurantGeoloc(pageID, headers, Lat, Lon):
    updateUrl = f"https://api.notion.com/v1/pages/{pageID}"
    updateData = {
        "properties": {
            "Geoloc": {
                "checkbox": True
                },
            "Lat": {
                "number": Lat
            },
            "Lon": {
                "number": Lon
            }
            }
        }
    data = json.dumps(updateData)
    response = requests.request("PATCH", updateUrl, headers=headers, data=data)
    print(response.status_code)



# Anonymisation param

# Opening JSON file
f = open("Param/param.json")

# returns JSON object as 
# a dictionary
param = json.load(f)

# Initialisation

token = param['Notion_API']['token']
databaseID = param['Notion_API']['databaseID']
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22"
}


# Fonctionnalité pour mettre à jour la geoloc des restaurants

def RestaurantGeoloc(databaseID, headers):

    # Récupération de la base Notion des restaurants

    readUrl = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(res.status_code)
    #print(res.text)


    # Geolocalisation

    # Création Geocoder Google
    locator = GoogleV3(api_key=param['GooglePlateform_API']['api_key'])

    RestaurantAdresse = {'ID':[], "Name" :[], "Adresse" :[], "Lat" :[], "Lon" :[]}


    for i in range(len(data['results'])):
        if data['results'][i]['properties']['Geoloc']['checkbox'] == False:
        
            RestaurantAdresse["ID"].append(data['results'][i]['id'])

            RestaurantAdresse["Name"].append(data['results'][i]['properties']['Name']['title'][0]['plain_text'])

            RestaurantAdresse["Adresse"].append(data['results'][i]['properties']['Adresse']['rich_text'][0]['text']['content'])

            location = locator.geocode(data['results'][i]['properties']['Adresse']['rich_text'][0]['text']['content'])

            if location == None:
                RestaurantAdresse["Lat"].append("tbd")

                RestaurantAdresse["Lon"].append("tbd")             

            else:
                RestaurantAdresse["Lat"].append(location.latitude)

                RestaurantAdresse["Lon"].append(location.longitude)                                

    # Mettre à jour la base notion



    ## Boucle de mise à jour geoloc

    for i in range(len(RestaurantAdresse["ID"])):
    
        pageID = RestaurantAdresse["ID"][i]
        Lat = RestaurantAdresse["Lat"][i]
        Lon = RestaurantAdresse["Lon"][i]
    
        updateRestaurantGeoloc(pageID, headers, Lat, Lon)


RestaurantGeoloc(databaseID, headers)
