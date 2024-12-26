import requests

# Define API endpoint and access token
api_url = "https://route-init.gallimap.com/api/v1/search/currentLocation"
access_token = "805e896e-209f-44a2-8a1d-28e8847dcdf4"  # Replace with your actual access token

# District you want to search
district_name = "Kathmandu"  # Replace with the district you want to search for

# Latitude and longitude of Nepal's approximate center (you can also use a more specific location)
nepal_lat = 28.3949
nepal_lng = 84.1240

# Keywords or features (you can define different features based on the API capabilities)
features = ["Attractions", "Parks", "Museums", "Heritage", "Libraries"]

def fetch_places(district_name):
    places = []

    for keyword in features:
        print(f"Fetching places for keyword: {keyword} in district: {district_name}")
        
        # API request parameters
        params = {
            "accessToken": access_token,
            "name": f"{keyword} {district_name}",  # Add district to the query
            "currentLat": nepal_lat,
            "currentLng": nepal_lng
        }
        
        # Make the request to the API
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract places from the response
            for feature in data.get('data', {}).get('features', []):
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [None, None])

                # Extract relevant information from each place
                place = {
                    "name": properties.get("searchedItem", "N/A"),
                    "province": properties.get("province", "N/A"),
                    "district": properties.get("district", district_name),
                    "municipality": properties.get("municipality", "N/A"),
                    "ward": properties.get("ward", "N/A"),
                    "longitude": coordinates[0] if coordinates and len(coordinates) > 0 else "N/A",
                    "latitude": coordinates[1] if coordinates and len(coordinates) > 1 else "N/A",
                    "feature": keyword  # Feature is based on the keyword being searched
                }
                
                places.append(place)
            print(f"Fetched {len(places)} places for keyword: {keyword}")
        else:
            print(f"Failed to fetch data for {keyword} in {district_name}. Status code: {response.status_code}")

    return places

# Fetch and display the places for a specific district
district_places = fetch_places(district_name)

# Print the places for verification
for place in district_places:
    print(place)
