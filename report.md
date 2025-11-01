
# Weather Forecasting App - Submission Package

## Overview
This project is a Weather Forecasting App built with **Flask** (backend) and a simple **HTML/CSS/JavaScript** frontend (Option B — stylish). It uses **XML** as the data interchange format between the client and server and demonstrates CRUD operations on saved cities. Live weather data is fetched from **OpenWeather API** (backend) and converted to XML before being sent to the client.

---

## Contents of the ZIP
- `app.py` — Flask backend application
- `cities.xml` — Starter XML storage for saved cities
- `templates/index.html` — Frontend HTML
- `static/css/style.css` — Frontend styling (Option B)
- `static/js/app.js` — Frontend JavaScript (sends/receives XML)
- `requirements.txt` — Python dependencies
- `report.md` — This file (User manual, developer doc, installation guide)

---

## User Manual (How to use)
1. Start the backend (see Installation). Open `http://localhost:5000` in your browser.
2. Search weather by typing a city name and clicking **Search**. The app will fetch live weather (backend calls OpenWeather and returns XML).
3. To **save a city**, type its name and click **Save City** — it will be stored in `cities.xml`.
4. View the **Saved Cities** table to edit, delete, or view saved cities' weather.

### Example Requests (XML)
- Create city (POST /cities):
```xml
<city><name>London</name></city>
```
- Update city (PUT /cities/1):
```xml
<city><name>New Name</name></city>
```

Responses are XML (e.g., `/weather/<city>` returns `<weather>...</weather>`)

---

## Developer Documentation (Design & Endpoints)
### Endpoints
- `GET /` — Serve frontend
- `GET /weather/<city_name>` — Fetch live weather (from OpenWeather), convert to XML, return it
- `GET /cities` — Return saved cities as XML
- `POST /cities` — Add a city (XML payload)
- `PUT /cities/<id>` — Update a city (XML payload)
- `DELETE /cities/<id>` — Delete a city

### Data Storage
Saved cities are stored in `cities.xml` with structure:
```xml
<cities>
  <city id="1"><name>...</name></city>
  ...
</cities>
```

### XML Usage
All inbound and outbound API payloads are XML. Backend uses `xml.etree.ElementTree` to parse and build XML and `xml.dom.minidom` for pretty printing.

---

## Installation Guide (Local)
1. Install Python 3.9+ and ensure `pip` is available.
2. (Optional) Create a virtualenv:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate   # Windows
```
3. Install requirements:
```bash
pip install -r requirements.txt
```
4. Set environment variable for OpenWeather API key (recommended):
```bash
export OPENWEATHER_API_KEY="your_api_key_here"   # macOS/Linux
setx OPENWEATHER_API_KEY "your_api_key_here"    # Windows (then reopen shell)
```
Or edit `app.py` and replace `YOUR_API_KEY_HERE` with your key (not recommended for submission).
5. Run the server:
```bash
python app.py
```
6. Open `http://localhost:5000` in your browser.

---

## Notes for Submission (CAMU)
- Zip the project folder and upload. The ZIP in this package is already prepared.
- Ensure `cities.xml` and `report.md` are included.
- Include your `report.md` in the submission as the documentation requested by the assignment.

---
Good luck! If you'd like, I can also:
- Add unit tests for the API
- Convert the backend to use a small SQLite DB but still expose XML
- Produce a ready-to-copy ZIP with a single download link (I already created one here)
