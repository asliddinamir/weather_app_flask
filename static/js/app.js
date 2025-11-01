
async function xmlFetch(url, options = {}){
  // default headers for XML
  options.headers = options.headers || {};
  if (!options.headers['Accept']) options.headers['Accept'] = 'application/xml';
  return fetch(url, options);
}

function parseXMLString(xmlText){
  return (new window.DOMParser()).parseFromString(xmlText, 'application/xml');
}

function getText(node, tag){
  const el = node.getElementsByTagName(tag)[0];
  return el ? el.textContent : '';
}

function showWeather(xmlDoc){
  const weather = xmlDoc.getElementsByTagName('weather')[0];
  if(!weather){
    const err = xmlDoc.getElementsByTagName('error')[0];
    const msg = err ? getText(err, 'message') : 'Unknown response';
    alert('Error: ' + msg);
    return;
  }
  const country = getText(weather, 'country');
  const city = getText(weather, 'city');
  const temp = getText(weather, 'temperature');
  const desc = getText(weather, 'description');
  const humidity = getText(weather, 'humidity');
  const wind = getText(weather, 'wind_speed');
  const cityInput = document.getElementById("city-input");
  const suggestions = document.getElementById("suggestions");


  const result = document.getElementById('weather-result');
  result.classList.remove('hidden');
  result.innerHTML = `
    <div class="weather-icon">☁️</div>
    <div class="weather-details">
      <h3>${city}, ${country}</h3>
      <p><strong>${temp}°C</strong> — ${desc}</p>
      <p>Humidity: ${humidity}% • Wind: ${wind} m/s</p>
    </div>
  `;
}

async function fetchWeather(city){
  const res = await xmlFetch('/weather/' + encodeURIComponent(city));
  const txt = await res.text();
  const xml = parseXMLString(txt);
  showWeather(xml);
}

async function loadCities(){
  const res = await xmlFetch('/cities');
  const txt = await res.text();
  const xml = parseXMLString(txt);
  const rows = xml.getElementsByTagName('city');
  const tbody = document.querySelector('#cities-table tbody');
  tbody.innerHTML = '';
  for(let i=0;i<rows.length;i++){
    const id = getText(rows[i], 'id') || rows[i].getAttribute('id');
    const name = getText(rows[i], 'name');
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${rows[i].getAttribute('id') || id}</td>
      <td>${name}</td>
      <td>
        <button class="action-btn edit-btn" data-id="${rows[i].getAttribute('id') || id}">Edit</button>
        <button class="action-btn del-btn" data-id="${rows[i].getAttribute('id') || id}">Delete</button>
        <button class="action-btn" data-city="${name}">View</button>
      </td>
    `;
    tbody.appendChild(tr);
  }

  // attach listeners
  document.querySelectorAll('.del-btn').forEach(b=>b.onclick = async (e)=>{
    const id = e.target.dataset.id;
    if(!confirm('Delete city id ' + id + '?')) return;
    const res = await xmlFetch('/cities/' + id, {method:'DELETE'});
    if(res.status===200) loadCities();
    else alert('Delete failed');
  });

  document.querySelectorAll('.edit-btn').forEach(b=>b.onclick = async (e)=>{
    const id = e.target.dataset.id;
    const newName = prompt('New city name:');
    if(!newName) return;
    const xml = `<city><name>${newName}</name></city>`;
    const res = await xmlFetch('/cities/' + id, {method:'PUT', body: xml, headers: {'Content-Type':'application/xml'}});
    if(res.status===200) loadCities();
    else alert('Update failed');
  });

  document.querySelectorAll('button[data-city]').forEach(b=>b.onclick = (e)=>{
    const city = e.target.dataset.city;
    document.getElementById('city-input').value = city;
    fetchWeather(city);
  });
}

document.getElementById('search-btn').onclick = ()=>{
  const city = document.getElementById('city-input').value.trim();
  if(!city) return alert('Type a city name');
  fetchWeather(city);
};

document.getElementById("city-input").addEventListener("keypress", function(e) {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("search-btn").click();
  }
});

document.getElementById('save-btn').onclick = async ()=>{
  const city = document.getElementById('city-input').value.trim();
  if(!city) return alert('Type a city name to save');
  const xml = `<city><name>${city}</name></city>`;
  const res = await xmlFetch('/cities', {method:'POST', body: xml, headers: {'Content-Type':'application/xml'}});
  if(res.status===201){ loadCities(); alert('City saved'); } else { const t=await res.text(); alert('Failed to save:\n'+t); }
};

// initial load
loadCities();
