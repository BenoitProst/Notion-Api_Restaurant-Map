from flask import Flask, render_template
# import connexion
import pandas as pd
import folium
import requests, json
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
from folium import IFrame
import branca
from folium import FeatureGroup, LayerControl, Map, Marker


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

    ## Création du dataframe

    RestaurantAdresseCarte = {'ID':[], "Name" :[], "Adresse" :[], "Lat" :[], "Lon" :[], "Atester_testé" :[], "Style" :[], "Lieu":[]}

    for i in range(len(data['results'])):
        if data['results'][i]['properties']['Geoloc']['checkbox'] == True:
            
            RestaurantAdresseCarte["ID"].append(data['results'][i]['id'])

            RestaurantAdresseCarte["Name"].append(data['results'][i]['properties']['Name']['title'][0]['plain_text'])

            RestaurantAdresseCarte["Adresse"].append(data['results'][i]['properties']['Adresse']['rich_text'][0]['text']['content'])

            RestaurantAdresseCarte["Lat"].append(data['results'][i]['properties']["Lat"]['number'])
        
            RestaurantAdresseCarte["Lon"].append(data['results'][i]['properties']["Lon"]['number'])
        
            RestaurantAdresseCarte["Atester_testé"].append(data['results'][i]['properties']['A tester / testé']['status']['name'])

            RestaurantAdresseCarte["Style"].append(data['results'][i]['properties']['Style']['multi_select'])
        
            RestaurantAdresseCarte["Lieu"].append(data['results'][i]['properties']['Lieu']['select']['name'])
    
    DfRestaurantAdresseCarte = pd.DataFrame.from_dict(RestaurantAdresseCarte)

    # Notion color HEX code
    NotionColorBG = {'default':'CECDCA',
                'gray':'EBECED',
                'brown':'E9E5E3',
                'orange':'FAEBDD',
                'yellow':'FBF3DB',
                'green':'DDEDEA',
                'blue':'DDEBF1',
                'purple':'EAE4F2',
                'pink':'F4DFEB',
                'red':'FBE4E4'}
    
    #Création de la fonction pour les popup
    def HtmlPopup(location_info):
        html = """ \
        <h5>"""+location_info['Name']+"""</h5><p style="line-height: 200%">"""
    

        for l in range(len(location_info['Style'])):
            html +="""<mark style="background: #"""
            html += NotionColorBG[location_info['Style'][l]['color']]
            html +=""" \
            !important"> """
            html += location_info['Style'][l]['name']
            html += """</mark>"""

        html += """</p>"""
    
        return html


    map = folium.Map(location=[DfRestaurantAdresseCarte.Lat.mean(), DfRestaurantAdresseCarte.Lon.mean()], zoom_start=14, tiles=None, control_scale=True)

    #Création des layercontrols
    GroupLieu = DfRestaurantAdresseCarte['Lieu'].drop_duplicates().sort_values().values

    GroupLieuDict ={}

    GroupLieuDict["All"] = FeatureGroup(name="All", overlay=False)
    folium.TileLayer(tiles='OpenStreetMap', location=[DfRestaurantAdresseCarte.Lat.mean(), DfRestaurantAdresseCarte.Lon.mean()]).add_to(GroupLieuDict["All"])
    GroupLieuDict["All"].add_to(map)


    for i in range(len(GroupLieu)):
    
        globals()[f"GroupLieu{i}"] = FeatureGroup(name=GroupLieu[i], overlay=False)
        location = [DfRestaurantAdresseCarte[DfRestaurantAdresseCarte["Lieu"]==GroupLieu[i]].Lat.mean(), DfRestaurantAdresseCarte[DfRestaurantAdresseCarte["Lieu"]==GroupLieu[i]].Lon.mean()]
    
        folium.TileLayer(tiles='OpenStreetMap', loaction=location).add_to(globals()[f"GroupLieu{i}"])
        GroupLieuDict[GroupLieu[i]] = globals()[f"GroupLieu{i}"]
        globals()[f"GroupLieu{i}"].add_to(map)
    
    
    #Plotting sur la carte
    
    for index, location_info in DfRestaurantAdresseCarte.iterrows():
        if location_info["Atester_testé"] == "A tester":
            folium.Marker([location_info["Lat"], location_info["Lon"]], popup=HtmlPopup(location_info), icon=folium.Icon(icon = 'utensils', prefix='fa', color ="lightgray")).add_to(GroupLieuDict["All"])
            folium.Marker([location_info["Lat"], location_info["Lon"]], popup=HtmlPopup(location_info), icon=folium.Icon(icon = 'utensils', prefix='fa', color ="lightgray")).add_to(GroupLieuDict[location_info['Lieu']])
    
        if location_info["Atester_testé"] == "Testé":
            folium.Marker([location_info["Lat"], location_info["Lon"]], popup=HtmlPopup(location_info), icon=folium.Icon(icon = 'utensils', prefix='fa', color ="green")).add_to(GroupLieuDict["All"])
            folium.Marker([location_info["Lat"], location_info["Lon"]], popup=HtmlPopup(location_info), icon=folium.Icon(icon = 'utensils', prefix='fa', color ="green")).add_to(GroupLieuDict[location_info['Lieu']])
        
        
    LayerControl().add_to(map)
    
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