from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

new_prius = {
    "TK2 14H", "TK2 21H", "TK2 30H", "TK2 37H", "TK2 41H", "TK2 44H", "TK2 88H",
    "TK2 91H", "TK2 93H", "TK2 94H", "TK1 52H", "TK1 58H", "TK1 64H", "TK1 77H",
    "TK1 81H", "TK1 84H", "TK1 91H", "TK1 98H", "EV0 65W", "EV0 71W", "EV0 79W",
    "VG5 72K", "VG3 88K", "SV6 98F", "SV6 83F", "SV7 18F", "SV7 42F", "SV7 69F", "SV7 74F"
}

model_colors = {
    "New Prius": "blue",
    "Prius": "green",
    "Prius C": "red",
    "Corolla": "orange",
    "Kia Niro EV": "violet",
    "Evolve eBike": "black"
}

def fetch_vehicle_data():
    oauth_url = 'https://java-us01.vulog.com/auth/realms/BCAA-CAYVR/protocol/openid-connect/token/'
    data = {
        'grant_type': 'client_credentials',
        'scope': '',
        'client_id': 'BCAA-CAYVR_anon',
        'client_secret': 'dbe490f4-2f4a-4bef-8c0b-52c0ecedb6c8'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip'
    }

    token_response = requests.post(oauth_url, data=data, headers=headers).json()
    access_token = token_response['access_token']

    data_url = 'https://java-us01.vulog.com/apiv5/availableVehicles/fc256982-77d1-455c-8ab0-7862c170db6a'
    headers1 = {
        'user-lat': '49.273351',
        'user-lon': '-123.102684',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Connection': 'close',
        'Authorization': f'bearer {access_token}',
        'X-API-Key': 'f52e5e56-c7db-4af0-acf5-0d8b13ac4bfc',
        'Host': 'java-us01.vulog.com',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.12.8'
    }

    response = requests.get(data_url, headers=headers1).json()

    for v in response:
        plate = v['description']['plate']
        if plate in new_prius:
            v['description']['model'] = "New Prius"

    return response

@app.route("/")
def map_view():
    selected_model = request.args.get("model", "All")
    data = fetch_vehicle_data()

    filtered = []
    for v in data:
        model = v["description"].get("model")
        if not model:
            continue
        if selected_model != "All" and model != selected_model:
            continue
        lat = v["location"]["position"]["lat"]
        lon = v["location"]["position"]["lon"]
        plate = v["description"]["plate"]
        filtered.append({
            "lat": lat,
            "lon": lon,
            "plate": plate,
            "model": model
        })

    return render_template("map_cluster.html",
                           vehicles=json.dumps(filtered),
                           model_colors=model_colors,
                           selected_model=selected_model,
                           model_options=["All"] + list(model_colors.keys()))

if __name__ == "__main__":
    app.run()
