#!/bin/bash

cd /root/Notion_api/Restaurant_Map

virtualenv -p /usr/bin/python3.11 venv

source venv/bin/activate

cd /root/Notion_api/Restaurant_Map/Notion-Api_Restaurant-Map

pip install -r requirements.txt

python ScriptRestaurantGeoloc.py

deactivate