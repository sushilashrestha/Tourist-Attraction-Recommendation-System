import sqlite3
import requests
import time

def get_place_details_with_opencage(name, city, country, lat, lon, api_url, api_key):
    """
    Extract the category and URL of a place using OpenCage API based on its latitude and longitude.

    Args:
        name (str): Name of the place.
        city (str): City name.
        country (str): Country name.
        lat (float): Latitude.
        lon (float): Longitude.
        api_url (str): Base URL of the OpenCage API.
        api_key (str): API key for OpenCage.

    Returns:
        tuple: (category, url) of the place if found, otherwise ("UnknownCategory", "UnknownURL").
    """
    params = {
        "q": f"{lat},{lon}",
        "key": api_key,
        "limit": 1
    }

    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["results"]:
            result = data["results"][0]
            category = result.get("components", {}).get("type", "UnknownCategory")  # Example key for category
            url = result.get("annotations", {}).get("url", "UnknownURL")  # Example key for URL
            return category, url
    else:
        print(f"Failed to fetch details for {name}: {response.status_code}, {response.text}")

    return "UnknownCategory", "UnknownURL"

def initialize_checkpoint_table(conn):
    """
    Ensure a checkpoint table exists in the database.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Checkpoint (
            TableName TEXT PRIMARY KEY,
            LastProcessedID INTEGER
        );
    """)
    conn.commit()

def get_last_checkpoint(conn, table_name):
    """
    Get the last processed ID for a table from the checkpoint table.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT LastProcessedID FROM Checkpoint WHERE TableName = ?;", (table_name,))
    result = cursor.fetchone()
    return result[0] if result else 0

def update_checkpoint(conn, table_name, last_processed_id):
    """
    Update the checkpoint table with the last processed ID.
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Checkpoint (TableName, LastProcessedID)
        VALUES (?, ?)
        ON CONFLICT(TableName) DO UPDATE SET LastProcessedID = ?;
    """, (table_name, last_processed_id, last_processed_id))
    conn.commit()

def create_new_table_with_place_details(
    db_path, old_table_name, new_table_name, api_url, api_key, checkpoint_interval=100
):
    """
    Create a new table and insert rows with place details using the OpenCage API.
    Includes checkpointing to allow resuming after interruptions.

    Args:
        db_path (str): Path to the SQLite database.
        old_table_name (str): Name of the old table.
        new_table_name (str): Name of the new table.
        api_url (str): OpenCage API base URL.
        api_key (str): API key for OpenCage.
        checkpoint_interval (int): Number of rows to process before committing changes to the database.
    """
    conn = sqlite3.connect(db_path)
    initialize_checkpoint_table(conn)

    # Get the last processed ID for resuming
    last_processed_id = get_last_checkpoint(conn, old_table_name)
    print(f"Resuming from ID {last_processed_id}")

    # Create the new table
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {new_table_name} (
            ID INTEGER PRIMARY KEY,
            Name TEXT,
            City TEXT,
            Country TEXT,
            Latitude REAL,
            Longitude REAL,
            Category TEXT,
            URL TEXT
        );
    """)

    # Fetch rows starting from the last processed ID
    cursor.execute(f"""
        SELECT ID, Name, City, Country, Latitude, Longitude
        FROM {old_table_name}
        WHERE ID > ?
        ORDER BY ID;
    """, (last_processed_id,))
    rows = cursor.fetchall()
    row_count = 0

    for row in rows:
        id_, name, city, country, lat, lon = row
        category, url = get_place_details_with_opencage(name, city, country, lat, lon, api_url, api_key)

        # Insert the row into the new table
        cursor.execute(f"""
            INSERT INTO {new_table_name} (ID, Name, City, Country, Latitude, Longitude, Category, URL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (id_, name, city, country, lat, lon, category, url))

        print(f"Inserted ID {id_}: Category = {category}, URL = {url}")
        row_count += 1
        last_processed_id = id_

        if row_count % checkpoint_interval == 0:
            conn.commit()
            update_checkpoint(conn, old_table_name, last_processed_id)
            print(f"Checkpoint saved: Last processed ID = {last_processed_id}")

        time.sleep(1)  # To avoid hitting API rate limits

    # Final commit and update checkpoint
    conn.commit()
    update_checkpoint(conn, old_table_name, last_processed_id)
    conn.close()
    print("New table with place details created and data inserted.")

# Example usage
if __name__ == "__main__":
    db_path = "tourist_attractions.db"  # Path to your SQLite database
    old_table_name = "First_Phase"  # Name of the old table
    new_table_name = "Second_Phase"  # Name of the new table with updated place details
    api_url = "https://api.opencagedata.com/geocode/v1/json"  # OpenCage API base URL
    api_key = "ff762592bde84b45a1480146adb508ce"  # Replace with your OpenCage API key

    create_new_table_with_place_details(db_path, old_table_name, new_table_name, api_url, api_key)
