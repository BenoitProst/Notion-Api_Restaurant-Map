from flask import Flask, render_template
# import connexion
import pandas as pd
import folium
import requests, json
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3

from ScriptRestaurantGeoloc import RestaurantGeoloc, updateRestaurantGeoloc

from apscheduler.schedulers.background import BackgroundScheduler


# Create the application instance
app = Flask(__name__)

scheduler = BackgroundScheduler(daemon=True)

#Création de la fonction pour créer les cartes
def RestaurantCreationMap(databaseID, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(res.status_code)

    with open('./full-properties.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)

    RestaurantAdresseCarte = {'ID':[], "Name" :[], "Adresse" :[], "Lat" :[], "Lon" :[]}


    for i in range(len(data['results'])):
        if data['results'][i]['properties']['Geoloc']['checkbox'] == True:
        
            RestaurantAdresseCarte["ID"].append(data['results'][i]['id'])

            RestaurantAdresseCarte["Name"].append(data['results'][i]['properties']['Name']['title'][0]['plain_text'])

            RestaurantAdresseCarte["Adresse"].append(data['results'][i]['properties']['Adresse']['rich_text'][0]['text']['content'])

            RestaurantAdresseCarte["Lat"].append(data['results'][i]['properties']["Lat"]['number'])
        
            RestaurantAdresseCarte["Lon"].append(data['results'][i]['properties']["Lon"]['number'])

    DfRestaurantAdresseCarte = pd.DataFrame.from_dict(RestaurantAdresseCarte)

    map = folium.Map(location=[DfRestaurantAdresseCarte.Lat.mean(), DfRestaurantAdresseCarte.Lon.mean()], zoom_start=14, control_scale=True)

    for index, location_info in DfRestaurantAdresseCarte.iterrows():
        folium.Marker([location_info["Lat"], location_info["Lon"]], popup=location_info["Name"]).add_to(map)

    map.save("templates/home.html")


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



# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
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

    RestaurantCreationMap(databaseID, headers)

    return render_template('home.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    
    scheduler.add_job(id = 'Scheduled Task', func=RestaurantGeoloc, args=[databaseID, headers], trigger='cron', hour='23')
    scheduler.start()
    
    app.run(host='0.0.0.0', port=5067, debug=True)