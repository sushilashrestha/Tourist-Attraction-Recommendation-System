import requests
import sqlite3
import pandas as pd
import time

# Function to fetch data for each place
def fetch_data_for_place(place):
    BASE_URL = "https://route-init.gallimap.com/api/v1/search/currentLocation"
    ACCESS_TOKEN = "805e896e-209f-44a2-8a1d-28e8847dcdf4"  # Replace with your actual token
    url = f"{BASE_URL}?accessToken={ACCESS_TOKEN}&name={place}&currentLat=27.5747&currentLng=85.4273"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Return the API response as a JSON object
    else:
        print(f"Failed to fetch data for {place}: {response.status_code}")
        return None

# Connect to SQLite database
conn = sqlite3.connect('Dataset/tourist_attractions.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS places (
    name TEXT,
    province TEXT,
    district TEXT,
    municipality TEXT,
    ward INTEGER,
    coordinates TEXT
)
''')

# Read places from CSV
df = pd.read_csv('nepal.csv')

# Loop through each place in the CSV file
batch_size = 10  # Checkpoint after every 10 places
for idx, Name in enumerate(df['Name']):
    print(f"Processing {Name}...")
    
    # Fetch the data from the API
    data = fetch_data_for_place(Name)
    
    if data and 'data' in data:
        # Check if 'features' exists in the response data
        features = data['data'].get('features', [])
        
        if features:
            for feature in features:
                # Safely extract the values from the 'properties' dictionary
                name = feature['properties'].get('searchedItem', 'Unknown Name')  # Default value if key is missing
                province = feature['properties'].get('province', 'Unknown Province')
                district = feature['properties'].get('district', 'Unknown District')
                municipality = feature['properties'].get('municipality', 'Unknown Municipality')
                
                # Check if 'geometry' and 'coordinates' are available
                coordinates = feature.get('geometry', {}).get('coordinates', None)
                
                # If coordinates are not available, log it
                if coordinates is None:
                    print(f"Coordinates not found for {name} ({district}, {province})")
                
                # Insert data into the database
                cursor.execute('''
                INSERT INTO places (name, province, district, municipality, ward, coordinates)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, province, district, municipality, None, str(coordinates)))
            
        else:
            print(f"No features found for {Name}")
    
    # Commit every 10 places as a checkpoint
    if (idx + 1) % batch_size == 0:
        conn.commit()
        print(f"Checkpoint reached at {idx + 1} places.")
    
    # Optional: Add delay to avoid rate limits
    time.sleep(1)

# Final commit for any remaining places
conn.commit()

# Close the database connection
conn.close()

print("Process completed!")
