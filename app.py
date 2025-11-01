
from flask import Flask, request, Response, send_from_directory, jsonify
import requests
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__, static_folder='static', template_folder='templates')

# Config: set OPENWEATHER_API_KEY as environment variable or put it here
API_KEY = os.getenv("OPENWEATHER_API_KEY")


DATA_FILE = Path('cities.xml')

def prettify_xml(elem):
    rough = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")

def ensure_datafile():
    if not DATA_FILE.exists():
        root = ET.Element('cities')
        tree = ET.ElementTree(root)
        tree.write(DATA_FILE, encoding='utf-8', xml_declaration=True)

def read_cities():
    ensure_datafile()
    tree = ET.parse(DATA_FILE)
    root = tree.getroot()
    cities = []
    for city in root.findall('city'):
        cities.append({
            'id': city.get('id'),
            'name': city.find('name').text if city.find('name') is not None else ''
        })
    return cities

def write_cities(cities):
    root = ET.Element('cities')
    for c in cities:
        city_el = ET.SubElement(root, 'city', id=str(c['id']))
        name_el = ET.SubElement(city_el, 'name')
        name_el.text = c['name']
    tree = ET.ElementTree(root)
    tree.write(DATA_FILE, encoding='utf-8', xml_declaration=True)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/weather/<city_name>', methods=['GET'])
def get_weather(city_name):
    # Fetch from OpenWeather (Current weather). Convert to XML and return.
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    resp = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
    if resp.status_code != 200:
        root = ET.Element('error')
        ET.SubElement(root, 'message').text = f'OpenWeather error: {resp.status_code}'
        return Response(prettify_xml(root), mimetype='application/xml', status=502)

    data = resp.json()
    root = ET.Element('weather')
    ET.SubElement(root, 'city').text = data.get('name', city_name)
    main = data.get('main', {})
    ET.SubElement(root, 'temperature').text = str(main.get('temp', ''))
    ET.SubElement(root, 'feels_like').text = str(main.get('feels_like', ''))
    ET.SubElement(root, 'humidity').text = str(main.get('humidity', ''))
    weather_list = data.get('weather', [])
    ET.SubElement(root, 'description').text = weather_list[0].get('description', '') if weather_list else ''
    wind = data.get('wind', {})
    ET.SubElement(root, 'wind_speed').text = str(wind.get('speed', ''))

    xml_str = prettify_xml(root)
    return Response(xml_str, mimetype='application/xml')

# CRUD for saved cities (stored in cities.xml)
@app.route('/cities', methods=['GET'])
def list_cities():
    cities = read_cities()
    root = ET.Element('cities')
    for c in cities:
        city_el = ET.SubElement(root, 'city', id=str(c['id']))
        ET.SubElement(city_el, 'name').text = c['name']
    return Response(prettify_xml(root), mimetype='application/xml')

@app.route('/cities', methods=['POST'])
def create_city():
    # Accept XML payload with <city><name>CityName</name></city>
    try:
        xml = ET.fromstring(request.data)
        name = xml.find('name').text if xml.find('name') is not None else None
        if not name:
            raise ValueError('Missing name element')
    except Exception as e:
        root = ET.Element('error')
        ET.SubElement(root, 'message').text = f'Invalid XML payload: {str(e)}'
        return Response(prettify_xml(root), mimetype='application/xml', status=400)

    cities = read_cities()
    next_id = 1 if not cities else max(int(c['id']) for c in cities) + 1
    cities.append({'id': str(next_id), 'name': name})
    write_cities(cities)
    root = ET.Element('result')
    ET.SubElement(root, 'message').text = 'City added'
    ET.SubElement(root, 'id').text = str(next_id)
    return Response(prettify_xml(root), mimetype='application/xml', status=201)

@app.route('/cities/<city_id>', methods=['PUT'])
def update_city(city_id):
    try:
        xml = ET.fromstring(request.data)
        name = xml.find('name').text if xml.find('name') is not None else None
        if not name:
            raise ValueError('Missing name element')
    except Exception as e:
        root = ET.Element('error')
        ET.SubElement(root, 'message').text = f'Invalid XML payload: {str(e)}'
        return Response(prettify_xml(root), mimetype='application/xml', status=400)

    cities = read_cities()
    found = False
    for c in cities:
        if c['id'] == city_id:
            c['name'] = name
            found = True
            break
    if not found:
        root = ET.Element('error')
        ET.SubElement(root, 'message').text = 'City not found'
        return Response(prettify_xml(root), mimetype='application/xml', status=404)

    write_cities(cities)
    root = ET.Element('result')
    ET.SubElement(root, 'message').text = 'City updated'
    return Response(prettify_xml(root), mimetype='application/xml')

@app.route('/cities/<city_id>', methods=['DELETE'])
def delete_city(city_id):
    cities = read_cities()
    new = [c for c in cities if c['id'] != city_id]
    if len(new) == len(cities):
        root = ET.Element('error')
        ET.SubElement(root, 'message').text = 'City not found'
        return Response(prettify_xml(root), mimetype='application/xml', status=404)
    write_cities(new)
    root = ET.Element('result')
    ET.SubElement(root, 'message').text = 'City deleted'
    return Response(prettify_xml(root), mimetype='application/xml')

if __name__ == "__main__":
    app.run(debug=True, port=5001)

