import sqlite3
import requests
import time

def get_city_from_coordinates(lat, lon, country, api_url, api_key):
    """
    Get the city name from latitude and longitude using a geocoding API,
    and include village, town, or any related locality term.
    
    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        country (str): Country name.
        api_url (str): Base URL of the geocoding API.
        api_key (str): API key for the geocoding service.
    
    Returns:
        str: City name, or other locality terms like village or town, if found; otherwise None.
    """
    params = {
        "q": f"{lat},{lon}",
        "key": api_key,
        "country": country,
        "format": "json"
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and "results" in data and data["results"]:
            for result in data["results"]:
                if "components" in result:
                    components = result["components"]
                    # Look for components like city, village, town, locality, etc.
                    locality_types = ['city', 'town', 'village', 'municipality', 'locality', 'state', 'district']
                    for locality in locality_types:
                        if locality in components:
                            return components[locality]
    return None

def create_new_table_with_updated_cities(
    db_path,
    old_table_name,
    new_table_name,
    api_url,
    api_keys,  # Changed from single api_key to a list of keys
    checkpoint_interval=100,
    resume_id=0
):
    """
    Create a new table and insert rows with updated city information using a geocoding API.
    
    Args:
        db_path (str): Path to the SQLite database.
        old_table_name (str): Name of the old table.
        new_table_name (str): Name of the new table.
        api_url (str): Geocoding API base URL.
        api_keys (list): List of geocoding API keys.
        checkpoint_interval (int): Number of rows to process before committing changes to the database.
        resume_id (int): ID to resume processing from.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the new table with the same structure as the old table, but with an additional City column
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {new_table_name} (
            ID INTEGER PRIMARY KEY,
            Name TEXT,
            Latitude REAL,
            Longitude REAL,
            Country TEXT,
            City TEXT
        );
    """)
    
    cursor.execute(f"SELECT MAX(ID) FROM {new_table_name}")
    last_inserted_id = cursor.fetchone()[0]
    if last_inserted_id is not None and last_inserted_id > resume_id:
        resume_id = last_inserted_id

    # Get rows from the old table where the City is 'Unknown' and ID is greater than resume_id
    cursor.execute(f"""
        SELECT ID, Name, Latitude, Longitude, Country
        FROM {old_table_name}
        WHERE City = 'Unknown' AND ID > ?;
    """, (resume_id,))
    rows = cursor.fetchall()
    row_count = 0

    not_found_count = 0
    api_key_index = 0
    current_api_key = api_keys[api_key_index]

    for row in rows:
        id, name, lat, lon, country = row
        city = get_city_from_coordinates(lat, lon, country, api_url, current_api_key)
        if city:
            # Insert the row into the new table with the updated city
            cursor.execute(f"""
                INSERT INTO {new_table_name} (ID, Name, Latitude, Longitude, Country, City)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (id, name, lat, lon, country, city))
            print(f"Inserted ID {id}: City = {city}")
            not_found_count = 0
        else:
            # Insert the row without updating the city if not found
            cursor.execute(f"""
                INSERT INTO {new_table_name} (ID, Name, Latitude, Longitude, Country, City)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (id, name, lat, lon, country, 'Unknown'))
            print(f"Could not find city for ID {id} (Lat: {lat}, Lon: {lon}, Country: {country})")
            not_found_count += 1
            if not_found_count >= 10:
                not_found_count = 0
                api_key_index += 1
                if api_key_index < len(api_keys):
                    current_api_key = api_keys[api_key_index]
                    print(f"Switched to next API key (index {api_key_index}).")
                else:
                    print("No more API keys available. Stopping process.")
                    break
        
        row_count += 1
        if row_count % checkpoint_interval == 0:
            conn.commit()
        time.sleep(1)  # To avoid hitting API rate limits

    conn.commit()
    conn.close()
    print("New table with updated cities created and data inserted.")

# Example usage
if __name__ == "__main__":
    db_path = "tourist_attractions.db"  # Path to your SQLite database
    old_table_name = "First_Phase"  # Name of the old table
    new_table_name = "First_Phase_Done"  # Name of the new table with updated city data
    api_url = "https://api.opencagedata.com/geocode/v1/json"  # OpenCage API base URL
    api_keys = [
        "a19fc0a8bac44f73a85892ce1ed0ed40",
        "f935c857d7e840c5841c41a1fe685d6c",
        "b80fef7cf9c94f38bd09f8aa28c66da7",
        "39e438131e794860bed31c931f804043",
        "9f42318e72fa4cdc96b92d6cd16feec4",
        "3aa17aaf6eab489e9052ace82aa50b97",
        "eb9b0d11fcdf4098a2b9292c2d7bd58f",
        "ff762592bde84b45a1480146adb508ce",
        "0b8992c140dd4b52b390add3e5b170f4",
        "d78ae1fc64f7469b84796c82231f3eec",
        "4011294deb5a487197489d618e15b8a3",
        "fc4caddb29c34dd498ab57ba82c19f32",
        "29d5d77e986047c89ff03a22d90bd8e4",
        "6f2123c5e00e4bd68a95ae61bbcaa070",
        "d5c0550e60e048a8bb477520df7bda79"
    ]

    create_new_table_with_updated_cities(db_path, old_table_name, new_table_name, api_url, api_keys)
