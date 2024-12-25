import pandas as pd
import re


import sqlite3  # SQLite database connector

# Database connection details
db_path = "Dataset/tourist_attractions.db"  # Path to your SQLite database file

# List of valid Asian countries
asian_countries = [
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", 
    "Cambodia", "China", "Cyprus", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", 
    "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", 
    "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine", 
    "Philippines", "Qatar", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", 
    "Tajikistan", "Thailand", "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates", 
    "Uzbekistan", "Vietnam", "Yemen"
]

# Helper functions
def clean_text_field(text):
    """Clean generic text fields like description or category."""
    if not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with one
    return text

def clean_name(name):
    """Clean and standardize attraction names."""
    name = clean_text_field(name)
    name = name.title()
    corrections = {
        "eiffel towerr": "Eiffel Tower", 
        "taj mahall": "Taj Mahal"
    }
    return corrections.get(name.lower(), name)

def clean_country(country):
    """Standardize country names and validate against Asian countries."""
    country = clean_text_field(country).title()
    return country if country in asian_countries else None  # Set to None if not valid

def clean_city(city):
    """Standardize city names."""
    city = clean_text_field(city)
    return city.title()

def clean_coordinates(lat, lon):
    """Ensure latitude and longitude are within valid ranges."""
    try:
        lat = float(lat)
        lon = float(lon)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon
        else:
            return None, None  # Return None for invalid coordinates
    except ValueError:
        return None, None

def clean_category(category):
    """Standardize category names."""
    category = clean_text_field(category)
    return category.title()

# Connect to SQLite database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

try:
    # Fetch data from Third_Phase table
    query = "SELECT id, name, country, city, latitude, longitude, category, description FROM Third_Phase"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Convert to DataFrame
    columns = ['id', 'name', 'country', 'city', 'latitude', 'longitude', 'category', 'description']
    df = pd.DataFrame(rows, columns=columns)

    # Clean fields
    df['name'] = df['name'].apply(clean_name)
    df['country'] = df['country'].apply(clean_country)
    df['city'] = df['city'].apply(clean_city)
    df[['latitude', 'longitude']] = df.apply(
        lambda row: pd.Series(clean_coordinates(row['latitude'], row['longitude'])), axis=1
    )
    df['category'] = df['category'].apply(clean_category)
    df['description'] = df['description'].apply(clean_text_field)

    # Create a new table for cleaned data
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cleaned_final (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        category TEXT,
        description TEXT
    )
    """
    cursor.execute(create_table_query)

    # Insert cleaned data into the new table
    insert_query = """
    INSERT INTO cleaned_final (id, name, country, city, latitude, longitude, category, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # Commit the changes
    connection.commit()
    print("Cleaned data has been successfully written to the 'cleaned_final' table.")

except Exception as e:
    print(f"An error occurred: {e}")
    connection.rollback()
finally:
    # Close the connection
    cursor.close()
    connection.close()
